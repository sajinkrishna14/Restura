
def load_menu(supabase, restaurant_id):
    response = (
        supabase.table("menu_items")
        .select(
            "id, name, malayalam_name, description, price, "
            "available, aliases"
        )
        .eq("restaurant_id", restaurant_id)
        .eq("available", True)
        .order("name")
        .execute()
    )
    return response.data or []


def add_item(cart: dict, item_id, quantity=1):
    key = str(item_id)
    cart[key] = min(50, max(1, int(cart.get(key, 0)) + int(quantity)))


def set_quantity(cart: dict, item_id, quantity):
    key = str(item_id)
    if key in cart:
        cart[key] = min(50, max(1, int(quantity)))


def remove_item(cart: dict, item_id):
    cart.pop(str(item_id), None)


def calculate_total(cart, menu_by_id):
    total = 0.0

    for item_id, quantity in cart.items():
        item = menu_by_id.get(str(item_id))
        if item:
            total += float(item["price"]) * int(quantity)

    return total


def save_order(
    supabase,
    restaurant_id,
    table_number,
    language,
    transcript,
    cart,
    menu_by_id,
):
    if not restaurant_id:
        raise ValueError("Select a restaurant before saving the order.")

    if not table_number or not transcript.strip() or not cart:
        raise ValueError(
            "Table number, transcript, and at least one item are required."
        )

    # Validate every cart item before creating the order.
    rows = []

    for item_id, quantity in cart.items():
        item = menu_by_id.get(str(item_id))

        if item is None:
            raise ValueError(
                f"Menu item {item_id} is no longer available."
            )

        if not item.get("available", True):
            raise ValueError(
                f"{item['name']} is currently unavailable."
            )

        quantity = int(quantity)
        if quantity < 1 or quantity > 50:
            raise ValueError("Quantity must be between 1 and 50.")

        rows.append({
            "menu_item_id": item["id"],
            "item_name": item["name"],
            "quantity": quantity,
            "unit_price": float(item["price"]),
        })

    # Associate this order with the selected restaurant.
    order_response = (
        supabase.table("orders")
        .insert({
            "restaurant_id": restaurant_id,
            "table_number": table_number,
            "language": language,
            "transcript": transcript.strip(),
            "status": "New",
        })
        .execute()
    )

    if not order_response.data:
        raise RuntimeError("Supabase did not return the created order.")

    order_id = order_response.data[0]["id"]

    for row in rows:
        row["order_id"] = order_id

    try:
        supabase.table("order_items").insert(rows).execute()
    except Exception:
        # Best-effort cleanup; this depends on database permissions.
        try:
            (
                supabase.table("orders")
                .delete()
                .eq("id", order_id)
                .eq("restaurant_id", restaurant_id)
                .execute()
            )
        except Exception:
            pass

        raise

    return order_id


def update_order_status(
    supabase,
    order_id,
    new_status,
    expected_status=None,
    restaurant_id=None,
):
    allowed_statuses = {"New", "Preparing", "Ready", "Delivered"}

    if new_status not in allowed_statuses:
        raise ValueError("Invalid order status.")

    query = (
        supabase.table("orders")
        .update({"status": new_status})
        .eq("id", order_id)
    )

    if restaurant_id:
        query = query.eq("restaurant_id", restaurant_id)

    if expected_status is not None:
        query = query.eq("status", expected_status)

    response = query.execute()

    if response.data:
        return response.data[0]

    raise RuntimeError(
        f"Order #{order_id} was not updated. It may have changed, "
        "or the order may not be accessible under the current session."
    )
