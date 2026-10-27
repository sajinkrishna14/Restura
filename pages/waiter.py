
import streamlit as st

from ui import apply_styles, render_section_title
from voice_service import transcribe_malayalam
from order_parser import match_transcript_to_menu
from restaurant_service import (
    load_menu,
    save_order,
    calculate_total,
    add_item,
    set_quantity,
    remove_item,
    update_order_status,
)
from auth_service import require_restaurant


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Restura | Waiter",
    page_icon="R",
    layout="wide",
)

apply_styles()

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1120px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    .waiter-brand {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }

    .brand-name {
        font-size: 1.8rem;
        font-weight: 750;
        letter-spacing: -1.3px;
        color: #174936;
    }

    .brand-name span {
        color: #77a88b;
    }

    .brand-meta {
        color: #69766e;
        font-size: .82rem;
        text-align: right;
    }

    .voice-panel {
        background: #ffffff;
        border: 1px solid #dfe8e1;
        border-radius: 22px;
        padding: 28px;
        margin: 8px 0 24px;
        box-shadow: 0 8px 28px rgba(23, 73, 54, .045);
    }

    .voice-kicker {
        color: #246b50;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        font-size: .72rem;
        font-weight: 750;
    }

    .voice-title {
        color: #174936;
        font-size: clamp(1.7rem, 3vw, 2.5rem);
        line-height: 1.12;
        font-weight: 750;
        letter-spacing: -1.2px;
        margin: 8px 0;
    }

    .voice-copy {
        color: #69766e;
        margin-bottom: 8px;
    }

    .order-total {
        border-radius: 16px;
        background: #174936;
        color: white;
        padding: 22px 24px;
        margin: 16px 0;
    }

    .order-total-label {
        font-size: .72rem;
        letter-spacing: 1.4px;
        color: #c9dfd2;
        font-weight: 700;
    }

    .order-total-value {
        font-size: 2rem;
        font-weight: 750;
        margin-top: 4px;
    }

    div[data-testid="stAudioInput"] {
        background: #f7faf7;
        border: 1px solid #dce8df;
        border-radius: 14px;
        padding: 12px;
    }

    div.stButton > button {
        border-radius: 11px;
        min-height: 44px;
        font-weight: 650;
        transition: transform .16s ease, background .16s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
    }

    div.stButton > button[kind="primary"] {
        background: #246b50;
        border-color: #246b50;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #174936;
        border-color: #174936;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e1e8e2;
        border-radius: 14px;
    }

    @media (max-width: 650px) {
        .block-container {
            padding: .8rem .7rem 2rem;
        }

        .voice-panel {
            padding: 18px;
            border-radius: 16px;
        }

        .brand-meta {
            text-align: right;
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


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def init_state():
    defaults = {
        "cart": {},
        "transcript": "",
        "speech_message": "",
        "order_saved_id": None,
        "save_error": "",
        "table_number": "",
        "order_language": "Malayalam",
        "last_matched_transcript": "",
        "last_match_count": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_order():
    # Clear order data without clearing authentication.
    st.session_state.cart = {}
    st.session_state.transcript = ""
    st.session_state.speech_message = ""
    st.session_state.order_saved_id = None
    st.session_state.save_error = ""
    st.session_state.table_number = ""
    st.session_state.order_language = "Malayalam"
    st.session_state.last_matched_transcript = ""
    st.session_state.last_match_count = 0

    # Clear quantity widgets from the previous order.
    for key in list(st.session_state.keys()):
        if key.startswith("quantity_"):
            del st.session_state[key]


init_state()


# --------------------------------------------------
# AUTHENTICATION AND RESTAURANT MENU
# --------------------------------------------------

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

try:
    gnani_api_key = st.secrets["GNANI_API_KEY"]
    menu = load_menu(supabase, restaurant_id)
except Exception as exc:
    st.error("Could not load the menu or Gnani settings.")
    st.code(f"{type(exc).__name__}: {exc}")
    st.stop()


st.markdown(
    f"""
    <div class="waiter-brand">
        <div class="brand-name">restura<span>.</span></div>
        <div class="brand-meta">
            {restaurant_name} · Waiter station
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if not menu:
    st.warning(
        "There are no available menu items in this restaurant. "
        "Add menu items in the owner interface first."
    )
    st.stop()


# Normalise IDs so parser results and cart keys match consistently.
menu_by_id = {
    str(item["id"]): item
    for item in menu
}


# Remove cart entries for menu items that are no longer available.
for item_id in list(st.session_state.cart.keys()):
    if str(item_id) not in menu_by_id:
        st.session_state.cart.pop(item_id, None)


# --------------------------------------------------
# VOICE ORDER CAPTURE
# --------------------------------------------------

st.markdown(
    """
    <div class="voice-panel">
        <div class="voice-kicker">Voice ordering · 01</div>
        <div class="voice-title">
            Take the order.<br>We'll handle the details.
        </div>
        <div class="voice-copy">
            Record the customer speaking in Malayalam,
            review the transcript, and match every recognised
            menu item before sending the order to the kitchen.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

voice_col, transcript_col = st.columns(
    [1, 1],
    gap="large",
)

with voice_col:
    st.markdown("#### Record customer order")

    audio = st.audio_input(
        "Tap to record in Malayalam",
        sample_rate=16000,
        key="waiter_audio_input",
    )

    if audio is not None:
        st.audio(audio, format="audio/wav")

        if st.button(
            "Transcribe recording",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.order_saved_id is not None,
        ):
            try:
                with st.spinner("Gnani is transcribing the order…"):
                    recognised_text = transcribe_malayalam(
                        audio,
                        gnani_api_key,
                    )

                st.session_state.transcript = recognised_text or ""
                st.session_state.speech_message = (
                    "Transcript ready. Review the text before matching."
                    if recognised_text
                    else "No speech was recognised. Please try again."
                )

                # A changed transcript must be matched again.
                st.session_state.last_matched_transcript = ""

                st.rerun()

            except Exception as exc:
                st.error("Gnani transcription failed.")
                st.code(f"{type(exc).__name__}: {exc}")

    if st.session_state.speech_message:
        st.info(st.session_state.speech_message)


with transcript_col:
    st.markdown("#### Review the transcript")

    st.text_area(
        "Transcript",
        key="transcript",
        height=155,
        placeholder=(
            "Recognised words appear here. "
            "You can correct the text before matching."
        ),
        disabled=st.session_state.order_saved_id is not None,
    )

    st.text_input(
        "Table number",
        key="table_number",
        placeholder="e.g. 04",
        disabled=st.session_state.order_saved_id is not None,
    )

    st.selectbox(
        "Order language",
        ["Malayalam", "Manglish", "English"],
        key="order_language",
        disabled=st.session_state.order_saved_id is not None,
    )

    if st.button(
        "Find menu items",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.order_saved_id is not None,
    ):
        current_transcript = st.session_state.transcript.strip()

        if not current_transcript:
            st.warning("Record or enter the customer's order first.")

        else:
            try:
                matches = match_transcript_to_menu(
                    current_transcript,
                    menu,
                )

                # Rebuild the cart from this transcript.
                # This avoids adding the same quantities repeatedly
                # when the waiter clicks the button more than once.
                new_cart = {}

                for item_id, quantity in matches.items():
                    item_id = str(item_id)

                    # Ignore results that do not belong to the loaded menu.
                    if item_id not in menu_by_id:
                        continue

                    quantity = max(1, min(int(quantity), 50))
                    new_cart[item_id] = quantity

                st.session_state.cart = new_cart
                st.session_state.last_matched_transcript = (
                    current_transcript
                )
                st.session_state.last_match_count = len(new_cart)

                # Clear old quantity widget state so displayed quantities
                # are synchronised with the newly matched cart.
                for key in list(st.session_state.keys()):
                    if key.startswith("quantity_"):
                        del st.session_state[key]

                if not new_cart:
                    st.session_state.speech_message = (
                        "No menu items matched this transcript. "
                        "Check the spelling, correct the transcript, "
                        "or add items manually below."
                    )
                else:
                    st.session_state.speech_message = (
                        f"Matched {len(new_cart)} distinct menu item(s). "
                        "Review the cart below before confirming."
                    )

                st.rerun()

            except Exception as exc:
                st.error("Could not match the transcript to the menu.")
                st.code(f"{type(exc).__name__}: {exc}")


# --------------------------------------------------
# CART AND MANUAL MENU SELECTION
# --------------------------------------------------

st.divider()

render_section_title(
    "02",
    "Build the order",
    "Add items and adjust quantities before confirming.",
)


if st.session_state.order_saved_id is None:
    add_col, add_button_col = st.columns([3, 1])

    with add_col:
        chosen_item = st.selectbox(
            "Choose a menu item",
            options=menu,
            format_func=lambda item: (
                f'{item["name"]} · ₹{float(item["price"]):.2f}'
            ),
            key="manual_menu_item",
        )

    with add_button_col:
        st.write("")

        if st.button(
            "Add item",
            use_container_width=True,
        ):
            item_id = str(chosen_item["id"])
            current_quantity = int(
                st.session_state.cart.get(item_id, 0)
            )

            if current_quantity >= 50:
                st.warning(
                    "This item has reached the quantity limit of 50."
                )
            else:
                add_item(
                    st.session_state.cart,
                    item_id,
                    1,
                )

                # Keep the stored cart quantity within the limit.
                st.session_state.cart[item_id] = min(
                    int(st.session_state.cart[item_id]),
                    50,
                )

                st.session_state.save_error = ""
                st.rerun()


# Keep only valid IDs from the currently available menu.
for item_id in list(st.session_state.cart.keys()):
    if str(item_id) not in menu_by_id:
        st.session_state.cart.pop(item_id, None)


cart = st.session_state.cart

if not cart:
    st.caption(
        "Your order is empty. Match the transcript or add an item manually."
    )

else:
    st.caption(
        f"{len(cart)} distinct menu item(s) in this order."
    )

    # No fixed three-item limit: render every cart entry.
    for item_id in list(cart.keys()):
        item_id = str(item_id)
        item = menu_by_id.get(item_id)

        if item is None:
            continue

        quantity = max(
            1,
            min(int(cart[item_id]), 50),
        )

        unit_price = float(item["price"])
        subtotal = quantity * unit_price

        with st.container(border=True):
            name_col, quantity_col, subtotal_col, remove_col = (
                st.columns(
                    [2.5, 1.1, 1.2, 0.9],
                    gap="small",
                )
            )

            with name_col:
                st.markdown(f"**{item['name']}**")
                st.caption(f"₹{unit_price:.2f} per item")

                malayalam_name = item.get("malayalam_name")
                if malayalam_name:
                    st.caption(str(malayalam_name))

            with quantity_col:
                new_quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=50,
                    value=quantity,
                    step=1,
                    key=f"quantity_{item_id}",
                    disabled=st.session_state.order_saved_id is not None,
                )

                if int(new_quantity) != quantity:
                    set_quantity(
                        st.session_state.cart,
                        item_id,
                        int(new_quantity),
                    )
                    st.rerun()

            with subtotal_col:
                st.caption("Subtotal")
                st.markdown(f"**₹{subtotal:,.2f}**")

            with remove_col:
                st.write("")

                if st.button(
                    "Remove",
                    key=f"remove_{item_id}",
                    disabled=st.session_state.order_saved_id is not None,
                ):
                    remove_item(
                        st.session_state.cart,
                        item_id,
                    )

                    st.session_state.pop(
                        f"quantity_{item_id}",
                        None,
                    )

                    st.rerun()

    total = calculate_total(
        st.session_state.cart,
        menu_by_id,
    )

    st.markdown(
        f"""
        <div class="order-total">
            <div class="order-total-label">ORDER TOTAL</div>
            <div class="order-total-value">₹{total:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# CONFIRM ORDER AND SAVE TO SUPABASE
# --------------------------------------------------

st.divider()

render_section_title(
    "03",
    "Confirm and send",
    "Only confirmed orders are sent to the kitchen.",
)


if st.session_state.order_saved_id is not None:
    st.success(
        f"Order #{st.session_state.order_saved_id} "
        "was saved successfully."
    )

    st.caption(
        "This order has been submitted. Start a new order "
        "to take the next customer's order."
    )

    if st.button(
        "Start a new order",
        type="primary",
        use_container_width=True,
    ):
        reset_order()
        st.rerun()

else:
    table_number = st.session_state.table_number.strip()
    transcript = st.session_state.transcript.strip()
    cart_has_items = bool(st.session_state.cart)

    ready_to_save = bool(
        table_number
        and transcript
        and cart_has_items
    )

    if not ready_to_save:
        st.caption(
            "Enter a table number, provide a transcript, and add "
            "at least one item before confirming."
        )

    if st.button(
        "Confirm order and send to kitchen",
        type="primary",
        use_container_width=True,
        disabled=not ready_to_save,
    ):
        try:
            # Validate the cart before submitting.
            validated_cart = {}

            for item_id, quantity in st.session_state.cart.items():
                item_id = str(item_id)

                if item_id not in menu_by_id:
                    raise ValueError(
                        f"Menu item {item_id} is no longer available."
                    )

                quantity = int(quantity)

                if quantity < 1 or quantity > 50:
                    raise ValueError(
                        f"Invalid quantity for {menu_by_id[item_id]['name']}."
                    )

                validated_cart[item_id] = quantity

            with st.spinner("Sending order to the kitchen…"):
                order_id = save_order(
                    supabase=supabase,
                    restaurant_id=restaurant_id,
                    table_number=table_number,
                    language=st.session_state.order_language,
                    transcript=transcript,
                    cart=validated_cart,
                    menu_by_id=menu_by_id,
                )

            st.session_state.order_saved_id = order_id
            st.session_state.save_error = ""
            st.rerun()

        except Exception as exc:
            st.session_state.save_error = (
                f"{type(exc).__name__}: {exc}"
            )

    if st.session_state.save_error:
        st.error("The order could not be saved.")
        st.code(st.session_state.save_error)
        st.caption(
            "Check Supabase before retrying, in case the order "
            "was saved but the app did not receive confirmation."
        )


# --------------------------------------------------
# KITCHEN STATUS UPDATES
# --------------------------------------------------

@st.fragment(run_every=15)
def ready_order_notifications():
    st.markdown("### Kitchen updates")

    try:
        response = (
            supabase.table("orders")
            .select("id, table_number, status, created_at")
            .eq("restaurant_id", restaurant_id)
            .eq("status", "Ready")
            .order("created_at")
            .execute()
        )

        ready_orders = response.data or []

    except Exception as exc:
        st.warning("Could not check kitchen updates.")
        st.caption(f"{type(exc).__name__}: {exc}")
        return

    if not ready_orders:
        st.caption("No orders are waiting for delivery.")
        return

    for order in ready_orders:
        order_id = order["id"]
        table_number = order.get("table_number", "—")

        with st.container(border=True):
            st.markdown(
                f"**Order #{order_id} · Table {table_number}**"
            )
            st.caption("The kitchen has marked this order ready.")

            if st.button(
                "Mark Delivered",
                key=f"delivered_{order_id}",
                type="primary",
            ):
                try:
                    update_order_status(
                        supabase,
                        order_id,
                        "Delivered",
                        expected_status="Ready",
                        restaurant_id=restaurant_id,
                    )

                    st.success(
                        f"Order #{order_id} marked delivered."
                    )
                    st.rerun()

                except Exception as exc:
                    st.error("Could not mark the order delivered.")
                    st.code(f"{type(exc).__name__}: {exc}")


ready_order_notifications()

st.caption(
    "Restura · Review the transcript and every item before confirmation."
)
