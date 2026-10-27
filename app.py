
import streamlit as st

st.set_page_config(
    page_title="Restura | Restaurant Management",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: #f7f9f6;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem 0 1.5rem 0;
    }

    .eyebrow {
        color: #27835b;
        font-weight: 700;
        letter-spacing: 2px;
        font-size: 0.8rem;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #183b2b;
        font-size: 3.2rem;
        line-height: 1.1;
        margin: 0.6rem 0;
    }

    .hero p {
        color: #66736a;
        font-size: 1.1rem;
        max-width: 650px;
    }

    div.stButton > button {
        background: #20734c;
        color: white;
        border: 1px solid #20734c;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        min-height: 3rem;
        width: 100%;
    }

    div.stButton > button:hover {
        background: #185b3b;
        border-color: #185b3b;
        color: white;
    }

    .role-card {
        background: white;
        border: 1px solid #e3e9e3;
        border-radius: 16px;
        padding: 1.5rem;
        min-height: 190px;
    }

    .role-card h3 {
        color: #183b2b;
        margin-bottom: 0.6rem;
    }

    .role-card p {
        color: #66736a;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Landing page ----------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Restaurant operations</div>
        <h1>Welcome to Restura.</h1>
        <p>
            One workspace for managing your menu, recording customer orders,
            and coordinating the kitchen.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.subheader("Choose your workspace")
st.caption("Open the interface you need to continue.")

owner, waiter, kitchen = st.columns(3, gap="large")

with owner:
    st.markdown(
        """
        <div class="role-card">
            <h3>Owner</h3>
            <p>Manage your restaurant workspace and menu items.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Owner", key="open_owner"):
        st.switch_page("pages/owner.py")

with waiter:
    st.markdown(
        """
        <div class="role-card">
            <h3>Waiter</h3>
            <p>Record spoken orders, review items, and send orders to the kitchen.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Waiter", key="open_waiter"):
        st.switch_page("pages/waiter.py")

with kitchen:
    st.markdown(
        """
        <div class="role-card">
            <h3>Kitchen</h3>
            <p>View incoming orders and update their preparation status.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Kitchen", key="open_kitchen"):
        st.switch_page("pages/kitchen.py")

st.divider()

st.caption("Restura · A shared restaurant ordering workspace")
