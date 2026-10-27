
import streamlit as st
from supabase import create_client


def get_supabase():
    """Create one authenticated Supabase client per Streamlit session."""
    if "restura_supabase" not in st.session_state:
        st.session_state.restura_supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )

    return st.session_state.restura_supabase


def login_screen():
    st.subheader("Sign in to Restura")

    with st.form("restura_login_form"):
        email = st.text_input("Restaurant account email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(
            "Log in",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not email.strip() or not password:
            st.error("Enter your email and password.")
            return

        try:
            client = get_supabase()
            response = client.auth.sign_in_with_password({
                "email": email.strip(),
                "password": password,
            })

            if not response.user or not response.session:
                st.error("Login failed. Please try again.")
                return

            st.session_state.restura_user = {
                "id": str(response.user.id),
                "email": response.user.email,
            }
            st.rerun()

        except Exception as exc:
            st.error("Login failed.")
            st.code(f"{type(exc).__name__}: {exc}")


def require_restaurant():
    """Authenticate the device and select a restaurant workspace."""
    if not st.session_state.get("restura_user"):
        login_screen()
        st.stop()

    client = get_supabase()
    user_id = st.session_state.restura_user["id"]

    try:
        memberships = (
            client.table("restaurant_members")
            .select("restaurant_id, role")
            .eq("user_id", user_id)
            .execute()
            .data or []
        )

        if not memberships:
            st.error(
                "This account is not linked to a restaurant. "
                "Ask the owner to add it to restaurant_members."
            )
            st.stop()

        restaurant_ids = list({
            row["restaurant_id"] for row in memberships
        })

        restaurants = (
            client.table("restaurants")
            .select("id, name")
            .in_("id", restaurant_ids)
            .execute()
            .data or []
        )

        if not restaurants:
            st.error(
                "No restaurant workspaces are accessible to this account. "
                "Check the restaurants and restaurant_members RLS policies."
            )
            st.stop()

        options = {
            f"{r['name']} · {str(r['id'])[:8]}": r
            for r in restaurants
        }

        selected = st.selectbox(
            "Restaurant workspace",
            options=list(options.keys()),
            key="restura_workspace_selection",
        )

        restaurant = options[selected]

        st.session_state.restaurant_id = str(restaurant["id"])
        st.session_state.restaurant_name = restaurant["name"]

        if st.button("Log out"):
            try:
                client.auth.sign_out()
            finally:
                for key in (
                    "restura_user",
                    "restaurant_id",
                    "restaurant_name",
                    "restura_supabase",
                    "restura_workspace_selection",
                ):
                    st.session_state.pop(key, None)
            st.rerun()

        return client, str(restaurant["id"])

    except Exception as exc:
        st.error("Could not load restaurant workspaces.")
        st.code(f"{type(exc).__name__}: {exc}")
        st.stop()
