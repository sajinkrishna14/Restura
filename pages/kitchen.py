
import streamlit as st
from gnani.tts import GnaniTTSClient

from auth_service import require_restaurant
from restaurant_service import update_order_status


st.set_page_config(
    page_title="Restura | Kitchen",
    page_icon="R",
    layout="wide",
)


# -------------------- DESIGN --------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --green: #246b50;
        --green-dark: #174936;
        --green-soft: #eaf3ed;
        --ink: #202a24;
        --muted: #69766e;
        --line: #e1e8e2;
        --page: #f6f8f6;
        --white: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--page);
        color: var(--ink);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }

    .kitchen-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        margin-bottom: 28px;
    }

    .brand {
        color: var(--green-dark);
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -1.2px;
    }

    .brand span {
        color: #77a88b;
    }

    .header-meta {
        color: var(--muted);
        font-size: .85rem;
        text-align: right;
    }

    .hero {
        background: var(--white);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 26px;
        box-shadow: 0 8px 28px rgba(23, 73, 54, .04);
    }

    .hero-label {
        color: var(--green);
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: 1.6px;
        text-transform: uppercase;
    }

    .hero-title {
        color: var(--green-dark);
        font-size: clamp(1.8rem, 3vw, 2.6rem);
        font-weight: 800;
        letter-spacing: -1.3px;
        line-height: 1.12;
        margin: 8px 0;
    }

    .hero-copy {
        color: var(--muted);
        margin: 0;
        font-size: .95rem;
    }

    .order-heading {
        color: var(--ink);
        font-size: 1.2rem;
        font-weight: 750;
        letter-spacing: -.3px;
        margin: 0 0 4px;
    }

    .order-subheading {
        color: var(--muted);
        font-size: .88rem;
        margin-bottom: 18px;
    }

    div.stButton > button {
        border-radius: 11px;
        min-height: 43px;
        font-weight: 650;
        transition: transform .16s ease, background .16s ease;
        border: 1px solid var(--line);
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
    }

    div.stButton > button[kind="primary"] {
        background: var(--green);
        border-color: var(--green);
        color: white;
    }

    div.stButton > button[kind="primary"]:hover {
        background: var(--green-dark);
        border-color: var(--green-dark);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--white);
        border-color: var(--line);
        border-radius: 16px;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    @media (max-width: 650px) {
        .block-container {
            padding: .8rem .7rem 2rem;
        }

        .hero {
            padding: 20px;
            border-radius: 15px;
        }

        .kitchen-header {
            align-items: flex-start;
        }

        .header-meta {
            max-width: 55%;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- AUTHENTICATION --------------------

try:
    supabase, restaurant_id = require_restaurant()
except Exception as exc:
    st.error("Could not open the restaurant workspace.")
    st.code(f"{type(exc).__name__}: {exc}")
    st.stop()

restaurant_name = st.session_state.get(
    "restaurant_name",
    "Restaurant",
)


# -------------------- SESSION STATE --------------------

if "announced_order_ids" not in st.session_state:
    st.session_state.announced_order_ids = set()

if "kitchen_audio_enabled" not in st.session_state:
    st.session_state.kitchen_audio_enabled = False


# -------------------- GNANI TEXT-TO-SPEECH --------------------

@st.cache_resource
def get_tts():
    return GnaniTTSClient(
        api_key=st.secrets["GNANI_API_KEY"]
    )


def announce_order(order, items):
    table_number = order.get("table_number", "unknown")

    lines = [
        f"ടേബിൾ നമ്പർ {table_number}.",
        "പുതിയ ഓർഡർ.",
    ]

    for item in items:
        name = item.get("item_name", "ഭക്ഷണ ഇനം")
        quantity = item.get("quantity", 1)
        lines.append(f"{name}, {quantity} എണ്ണം.")

    announcement = " ".join(lines)

    client = get_tts()

    return client.synthesize(
        announcement,
        voice="Kaveri",
        model="timbre-v2.5",
        language="ml-IN",
    )


# -------------------- DATABASE FUNCTIONS --------------------

def fetch_active_orders():
    response = (
        supabase.table("orders")
        .select(
            "id, restaurant_id, table_number, status, "
            "created_at, language, transcript"
        )
        .eq("restaurant_id", restaurant_id)
        .in_("status", ["New", "Preparing"])
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def fetch_order_items(order_id):
    response = (
        supabase.table("order_items")
        .select("order_id, item_name, quantity, unit_price")
        .eq("order_id", order_id)
        .execute()
    )

    return response.data or []


# -------------------- PAGE HEADER --------------------

st.markdown(
    f"""
    <div class="kitchen-header">
        <div class="brand">restura<span>.</span></div>
        <div class="header-meta">
            {restaurant_name}<br>
            Kitchen station
        </div>
    </div>

    <section class="hero">
        <div class="hero-label">Live order management</div>
        <div class="hero-title">The kitchen, in sync.</div>
        <p class="hero-copy">
            View incoming orders, hear Malayalam announcements,
            and update preparation status.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# -------------------- AUDIO CONTROL --------------------

audio_col, info_col = st.columns([1, 2], gap="large")

with audio_col:
    if not st.session_state.kitchen_audio_enabled:
        if st.button(
            "Enable kitchen audio",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.kitchen_audio_enabled = True
            st.rerun()
    else:
        st.success("Kitchen audio enabled")

with info_col:
    st.caption(
        "New orders can be announced aloud in Malayalam. "
        "Keep this page open to receive live updates."
    )


# -------------------- LIVE ORDERS --------------------

@st.fragment(run_every=20)
def kitchen_orders():
    st.markdown(
        '<div class="order-heading">Active orders</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="order-subheading">'
        'Orders currently waiting for preparation or completion.'
        '</div>',
        unsafe_allow_html=True,
    )

    try:
        orders = fetch_active_orders()
    except Exception as exc:
        st.error("Could not load orders from Supabase.")
        st.code(f"{type(exc).__name__}: {exc}")
        return

    # Announce the newest unseen order, one per refresh.
    unseen_orders = [
        order
        for order in orders
        if order.get("status") == "New"
        and order.get("id")
        not in st.session_state.announced_order_ids
    ]

    if unseen_orders and st.session_state.kitchen_audio_enabled:
        order_to_announce = unseen_orders[-1]
        order_id = order_to_announce["id"]

        try:
            items = fetch_order_items(order_id)
            audio = announce_order(order_to_announce, items)

            st.markdown("#### New order announcement")
            st.audio(audio, format="audio/wav", autoplay=True)

            st.session_state.announced_order_ids.add(order_id)

        except Exception as exc:
            st.warning(
                "A new order arrived, but its voice announcement failed."
            )
            st.code(f"{type(exc).__name__}: {exc}")

    if not orders:
        st.info(
            "No active orders right now. New orders will appear here "
            "automatically."
        )
        return

    for order in orders:
        order_id = order["id"]
        status = order.get("status", "New")
        table_number = order.get("table_number", "—")

        try:
            items = fetch_order_items(order_id)
        except Exception as exc:
            st.warning(f"Could not load items for order #{order_id}.")
            st.caption(f"{type(exc).__name__}: {exc}")
            continue

        with st.container(border=True):
            details_col, action_col = st.columns(
                [3, 1],
                gap="large",
            )

            with details_col:
                st.markdown(
                    f"### Order #{order_id} · Table {table_number}"
                )

                if status == "New":
                    st.info("New order")
                elif status == "Preparing":
                    st.warning("Preparing")

                if order.get("created_at"):
                    st.caption(f"Received: {order['created_at']}")

                st.markdown("**Items**")

                if items:
                    for item in items:
                        name = item.get("item_name", "Item")
                        quantity = item.get("quantity", 1)
                        unit_price = float(item.get("unit_price") or 0)
                        st.write(
                            f"{name}  ×  {quantity}  ·  "
                            f"₹{unit_price * int(quantity):,.2f}"
                        )
                else:
                    st.caption("No order items were found.")

                if order.get("transcript"):
                    with st.expander("Original waiter transcript"):
                        st.write(order["transcript"])

            with action_col:
                if status == "New":
                    if st.button(
                        "Start preparing",
                        key=f"prepare_{order_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        try:
                            update_order_status(
                                supabase,
                                order_id,
                                "Preparing",
                                expected_status="New",
                                restaurant_id=restaurant_id,
                            )
                            st.rerun()
                        except Exception as exc:
                            st.error("Could not update the order.")
                            st.code(f"{type(exc).__name__}: {exc}")

                elif status == "Preparing":
                    if st.button(
                        "Mark ready",
                        key=f"ready_{order_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        try:
                            update_order_status(
                                supabase,
                                order_id,
                                "Ready",
                                expected_status="Preparing",
                                restaurant_id=restaurant_id,
                            )
                            st.rerun()
                        except Exception as exc:
                            st.error("Could not update the order.")
                            st.code(f"{type(exc).__name__}: {exc}")


kitchen_orders()

st.caption(
    "Restura prototype · Orders are scoped to the selected restaurant."
)
