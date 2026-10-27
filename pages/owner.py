
import streamlit as st
from supabase import create_client


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Restura | Owner Portal",
    page_icon="R",
    layout="wide",
)


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #f5f7f2;
    }

    .main-title {
        color: #173b2b;
        font-size: 2.3rem;
        font-weight: 750;
        margin-bottom: 0;
    }

    .subtitle {
        color: #647568;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background-color: #236b48;
        border-color: #236b48;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">Restura</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Restaurant workspace and menu management</div>',
    unsafe_allow_html=True,
)


# =========================================================
# SUPABASE CLIENT
# One client per Streamlit browser session
# =========================================================

def get_supabase():
    if "restura_supabase" not in st.session_state:
        st.session_state.restura_supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )

    return st.session_state.restura_supabase


try:
    supabase = get_supabase()
except Exception as exc:
    st.error(
        "Could not connect to Supabase. Check your "
        ".streamlit/secrets.toml settings."
    )
    st.caption(f"{type(exc).__name__}: {exc}")
    st.stop()


# =========================================================
# SESSION STATE
# =========================================================

if "owner_user" not in st.session_state:
    st.session_state.owner_user = None

if "restaurant_id" not in st.session_state:
    st.session_state.restaurant_id = None

if "restaurant_name" not in st.session_state:
    st.session_state.restaurant_name = None


def clear_workspace():
    st.session_state.restaurant_id = None
    st.session_state.restaurant_name = None


def log_out():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    for key in (
        "owner_user",
        "restaurant_id",
        "restaurant_name",
        "restura_supabase",
        "workspace_selector",
    ):
        st.session_state.pop(key, None)

    st.rerun()


# =========================================================
# LOGIN AND REGISTRATION
# =========================================================

def authentication_screen():
    st.subheader("Welcome to Restura")
    st.write(
        "Sign in to manage your restaurant or create a new account."
    )

    login_tab, register_tab = st.tabs(
        ["Log in", "Create account"]
    )

    with login_tab:
        with st.form("login_form"):
            email = st.text_input(
                "Email address",
                key="login_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            submitted = st.form_submit_button(
                "Log in",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not email.strip() or not password:
                st.error("Enter both your email and password.")
            else:
                try:
                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": email.strip(),
                            "password": password,
                        }
                    )

                    if not response.user or not response.session:
                        st.error("Login failed. Please try again.")
                    else:
                        st.session_state.owner_user = {
                            "id": str(response.user.id),
                            "email": response.user.email,
                        }

                        clear_workspace()
                        st.rerun()

                except Exception:
                    st.error(
                        "Login failed. Check your credentials and "
                        "whether your email has been confirmed."
                    )

    with register_tab:
        with st.form("register_form"):
            new_email = st.text_input(
                "Email address",
                key="register_email",
            )

            new_password = st.text_input(
                "Password",
                type="password",
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="register_confirm_password",
            )

            register = st.form_submit_button(
                "Create account",
                type="primary",
                use_container_width=True,
            )

        if register:
            if not new_email.strip() or not new_password:
                st.error("Enter an email address and password.")

            elif len(new_password) < 8:
                st.error("Use a password with at least 8 characters.")

            elif new_password != confirm_password:
                st.error("The passwords do not match.")

            else:
                try:
                    response = supabase.auth.sign_up(
                        {
                            "email": new_email.strip(),
                            "password": new_password,
                        }
                    )

                    if response.session and response.user:
                        st.session_state.owner_user = {
                            "id": str(response.user.id),
                            "email": response.user.email,
                        }

                        clear_workspace()
                        st.success("Account created.")
                        st.rerun()

                    else:
                        st.success(
                            "Registration submitted. Check your email "
                            "to confirm your account, then log in."
                        )

                except Exception:
                    st.error(
                        "Registration failed. The email may already "
                        "exist, or Supabase authentication settings "
                        "may need checking."
                    )


# Require login before accessing workspace data.
if not st.session_state.owner_user:
    authentication_screen()
    st.stop()


# =========================================================
# LOAD AUTHENTICATED USER AND RESTAURANT WORKSPACES
# =========================================================

user = st.session_state.owner_user

st.caption(f"Signed in as {user['email']}")

header_left, header_right = st.columns([4, 1])

with header_right:
    if st.button("Log out", use_container_width=True):
        log_out()

try:
    memberships_response = (
        supabase.table("restaurant_members")
        .select("restaurant_id, role")
        .eq("user_id", user["id"])
        .execute()
    )

    memberships = memberships_response.data or []

    restaurant_ids = list(
        {
            str(row["restaurant_id"])
            for row in memberships
        }
    )

    if restaurant_ids:
        restaurants_response = (
            supabase.table("restaurants")
            .select("id, name")
            .in_("id", restaurant_ids)
            .execute()
        )

        restaurants = restaurants_response.data or []
    else:
        restaurants = []

except Exception as exc:
    st.error("Could not load your restaurant workspaces.")
    st.caption(f"{type(exc).__name__}: {exc}")
    st.stop()


# =========================================================
# CREATE WORKSPACE IF USER HAS NONE
# =========================================================

if not restaurants:
    st.subheader("Create your restaurant workspace")

    st.write(
        "A workspace keeps your restaurant's menu and orders "
        "separate from other restaurants."
    )

    with st.form("create_workspace_form"):
        restaurant_name_input = st.text_input(
            "Restaurant name",
            placeholder="e.g. Restura Demo",
        )

        create_workspace = st.form_submit_button(
            "Create workspace",
            type="primary",
        )

    if create_workspace:
        restaurant_name_input = restaurant_name_input.strip()

        if len(restaurant_name_input) < 2:
            st.error(
                "Enter a restaurant name with at least 2 characters."
            )

        else:
            try:
                result = supabase.rpc(
                    "create_restaurant_workspace",
                    {
                        "restaurant_name": restaurant_name_input,
                    },
                ).execute()

                new_id = result.data

                if isinstance(new_id, list):
                    new_id = new_id[0] if new_id else None

                if isinstance(new_id, dict):
                    new_id = new_id.get(
                        "create_restaurant_workspace"
                    )

                if not new_id:
                    st.error(
                        "Workspace creation returned no ID. "
                        "Check the create_restaurant_workspace "
                        "function in Supabase."
                    )
                else:
                    st.session_state.restaurant_id = str(new_id)
                    st.success("Workspace created.")
                    st.rerun()

            except Exception as exc:
                st.error("Could not create the workspace.")
                st.caption(f"{type(exc).__name__}: {exc}")

    st.stop()


# =========================================================
# SELECT WORKSPACE
# =========================================================

restaurant_options = {
    f"{row['name']} · {str(row['id'])[:8]}": row
    for row in restaurants
}

option_labels = list(restaurant_options.keys())

current_label = next(
    (
        label
        for label, row in restaurant_options.items()
        if str(row["id"])
        == str(st.session_state.restaurant_id)
    ),
    option_labels[0],
)

selected_label = st.selectbox(
    "Restaurant workspace",
    options=option_labels,
    index=option_labels.index(current_label),
    key="workspace_selector",
)

selected_restaurant = restaurant_options[selected_label]

restaurant_id = str(selected_restaurant["id"])
restaurant_name = selected_restaurant["name"]

st.session_state.restaurant_id = restaurant_id
st.session_state.restaurant_name = restaurant_name

current_membership = next(
    (
        membership
        for membership in memberships
        if str(membership["restaurant_id"]) == restaurant_id
    ),
    None,
)

if not current_membership:
    st.error("Your account is not a member of this workspace.")
    st.stop()

role = current_membership["role"]

st.success(f"Workspace: {restaurant_name}")
st.caption(f"Your role: {role}")


# =========================================================
# MENU HELPERS
# =========================================================

def parse_aliases(value):
    return list(
        dict.fromkeys(
            alias.strip()
            for alias in value.replace("\n", ",").split(",")
            if alias.strip()
        )
    )


def load_restaurant_menu():
    response = (
        supabase.table("menu_items")
        .select(
            "id, name, malayalam_name, description, price, "
            "available, aliases"
        )
        .eq("restaurant_id", restaurant_id)
        .order("name")
        .execute()
    )

    return response.data or []


# =========================================================
# MENU MANAGEMENT
# =========================================================

st.divider()
st.subheader("Menu management")

st.write(
    "Enter both names so the waiter can identify menu items "
    "from English, Malayalam, and Manglish speech."
)

if role != "owner":
    st.info("Only restaurant owners can manage the menu.")
    st.stop()


add_tab, edit_tab = st.tabs(
    ["Add menu item", "Edit existing item"]
)


# ---------------------------------------------------------
# ADD MENU ITEM
# ---------------------------------------------------------

with add_tab:
    with st.form("add_menu_item_form"):
        english_name = st.text_input(
            "English name *",
            placeholder="Masala dosa",
        )

        malayalam_name = st.text_input(
            "Malayalam name *",
            placeholder="മസാല ദോശ",
        )

        price = st.number_input(
            "Price (₹) *",
            min_value=0.01,
            max_value=100000.00,
            value=50.00,
            step=5.00,
        )

        description = st.text_input(
            "Description (optional)",
        )

        aliases_text = st.text_area(
            "Spoken aliases (comma-separated)",
            placeholder="masala dosha, masala dosa, മസാല ദോശ",
            help=(
                "Include Manglish spellings and common "
                "spoken variations."
            ),
        )

        available = st.checkbox(
            "Available for ordering",
            value=True,
        )

        add_submitted = st.form_submit_button(
            "Save menu item",
            type="primary",
            use_container_width=True,
        )

    if add_submitted:
        if not english_name.strip() or not malayalam_name.strip():
            st.error(
                "Both English and Malayalam names are required."
            )

        else:
            try:
                payload = {
                    "restaurant_id": restaurant_id,
                    "name": english_name.strip(),
                    "malayalam_name": malayalam_name.strip(),
                    "description": description.strip(),
                    "price": float(price),
                    "available": available,
                    "aliases": parse_aliases(aliases_text),
                }

                supabase.table("menu_items").insert(
                    payload
                ).execute()

                st.success("Menu item saved.")
                st.rerun()

            except Exception as exc:
                st.error("Could not save the menu item.")
                st.caption(f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------
# EDIT MENU ITEM
# ---------------------------------------------------------

with edit_tab:
    try:
        menu_items = load_restaurant_menu()

    except Exception as exc:
        st.error("Could not load your menu.")
        st.caption(f"{type(exc).__name__}: {exc}")
        menu_items = []

    if not menu_items:
        st.info(
            "No menu items yet. Add your first item in the other tab."
        )

    else:
        item_labels = {
            (
                f"{item['name']} · ₹{float(item['price']):.2f} "
                f"· ID {item['id']}"
            ): item
            for item in menu_items
        }

        chosen_label = st.selectbox(
            "Choose a menu item",
            options=list(item_labels.keys()),
        )

        chosen = item_labels[chosen_label]

        with st.form("edit_menu_item_form"):
            edit_name = st.text_input(
                "English name",
                value=chosen.get("name") or "",
            )

            edit_malayalam = st.text_input(
                "Malayalam name",
                value=chosen.get("malayalam_name") or "",
            )

            edit_price = st.number_input(
                "Price (₹)",
                min_value=0.01,
                max_value=100000.00,
                value=max(
                    0.01,
                    float(chosen.get("price") or 0.01),
                ),
                step=5.00,
            )

            edit_description = st.text_input(
                "Description",
                value=chosen.get("description") or "",
            )

            aliases = chosen.get("aliases") or []

            edit_aliases = st.text_area(
                "Spoken aliases (comma-separated)",
                value=", ".join(aliases),
            )

            edit_available = st.checkbox(
                "Available for ordering",
                value=bool(chosen.get("available", True)),
            )

            save_changes = st.form_submit_button(
                "Save changes",
                type="primary",
            )

        if save_changes:
            if not edit_name.strip() or not edit_malayalam.strip():
                st.error(
                    "Both English and Malayalam names are required."
                )

            else:
                try:
                    (
                        supabase.table("menu_items")
                        .update(
                            {
                                "name": edit_name.strip(),
                                "malayalam_name": edit_malayalam.strip(),
                                "price": float(edit_price),
                                "description": edit_description.strip(),
                                "aliases": parse_aliases(edit_aliases),
                                "available": edit_available,
                            }
                        )
                        .eq("id", chosen["id"])
                        .eq("restaurant_id", restaurant_id)
                        .execute()
                    )

                    st.success("Menu item updated.")
                    st.rerun()

                except Exception as exc:
                    st.error("Could not update the menu item.")
                    st.caption(f"{type(exc).__name__}: {exc}")

        st.warning(
            "To temporarily remove an item from ordering, "
            "uncheck 'Available for ordering' and save changes."
        )

        # -------------------------------------------------
        # PERMANENTLY DELETE MENU ITEM
        # -------------------------------------------------

        with st.expander("Permanently delete this menu item"):
            st.write(
                "This removes the menu item. Historical order "
                "records should retain their saved names and prices."
            )

            confirm_delete = st.checkbox(
                f"Confirm deletion of {chosen['name']}",
                key=f"confirm_delete_{chosen['id']}",
            )

            if st.button(
                "Delete menu item",
                type="secondary",
                disabled=not confirm_delete,
            ):
                try:
                    (
                        supabase.table("menu_items")
                        .delete()
                        .eq("id", chosen["id"])
                        .eq("restaurant_id", restaurant_id)
                        .execute()
                    )

                    st.success("Delete request completed.")
                    st.rerun()

                except Exception as exc:
                    st.error("Could not delete the menu item.")
                    st.caption(f"{type(exc).__name__}: {exc}")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Restura · Owner Portal · Menu data is scoped to "
    "the selected workspace."
)
