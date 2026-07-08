# ui/components.py
# Renders UI elements using native Streamlit components

import streamlit as st

from services.inventory_service import Inventory
from services.backup_service import save_and_backup


# ==============================================================================
# STYLING
# ==============================================================================

def _style_status(val: str) -> str:
    colors = {
        "IN STOCK":  "background-color: #22C55E; color: black;",    # Soft green
        "LOW STOCK": "background-color: #FDE047; color: black;",    # Soft yellow
        "NO STOCK":  "background-color: #EF4444; color: black;",    # Soft red
    }
    return colors.get(val, "")


# ==============================================================================
# TYPOGRAPHY
# ==============================================================================

def header(title: str, icon: str = "") -> None:
    label = f"{icon} {title}" if icon else title
    st.subheader(label)


# ==============================================================================
# METRICS
# ==============================================================================

def metric_row(total_items: int, stock: int, location: str) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 ITEMS",    total_items)
    c2.metric("🗃️ STOCK",    stock)
    c3.metric("📍 LOCATION", location)


# ==============================================================================
# SHUTDOWN SCREEN
# ==============================================================================

def shutdown_screen() -> None:
    st.title("SIMS Server Disconnected")
    st.write("You may close this browser tab.")


# ==============================================================================
# TAB RENDERERS
# ==============================================================================

def _commit(inventory: Inventory, msg: str) -> None:
    # Persist changes, show feedback, and trigger a Streamlit rerun
    backup = save_and_backup(inventory)
    st.success(msg)
    st.caption(f"💾 Backup saved: `{backup}`")
    st.rerun()


def render_view_tab(inventory: Inventory, location: str) -> None:
    header("Metrics Overview", "📊")

    display_df = inventory.filtered(location)
    if display_df.empty:
        st.warning("No inventory found.")
        return

    stock = int(display_df["QUANTITY"].sum())
    metric_row(display_df["ITEM"].nunique(), stock, location)

    row_height    = 35
    header_height = 38
    styled_df     = display_df.style.map(_style_status, subset=["STATUS"])

    st.dataframe(
        styled_df,
        width='stretch',
        hide_index=True,
        height=(len(display_df) * row_height) + header_height,
    )


def render_edit_tab(inventory: Inventory) -> None:
    col_add, col_remove = st.columns(2)

    with col_add:
        header("ADD / EDIT", "➕")

        with st.form("add_form", clear_on_submit=True):
            item_id  = st.number_input("ID",       min_value=1, value=1000)
            item     = st.text_input("Item Name").strip().upper()
            category = st.text_input("Category").strip().upper()
            qty      = st.number_input("Quantity", min_value=1, value=5)
            cost     = st.text_input("Cost",       value="$1.00")
            price    = st.text_input("Price",      value="$2.50")
            location = st.text_input("Location").strip().upper()

            if st.form_submit_button("SAVE") and item and location:
                try:
                    inventory.add_or_edit(
                        item_id, item, category, qty, cost, price, location
                    )
                    _commit(inventory, f"Processed {item} at {location}.")
                except ValueError as exc:
                    st.error(str(exc))

    with col_remove:
        header("Adjust Stock", "➖")

        if inventory.df.empty:
            st.info("No items available.")
            return

        with st.form("remove_form", clear_on_submit=True):
            labels   = inventory.selector_labels()
            selected = st.selectbox("Select Item", labels.unique())

            target  = inventory.df.loc[labels == selected].iloc[0]
            max_qty = int(target["QUANTITY"])

            qty = st.number_input(
                f"Quantity (Max: {max_qty})",
                min_value=1,
                max_value=max_qty,
            )

            if st.form_submit_button("Deduct Stock"):
                inventory.record_sale(target["ID"], target["LOCATION"], qty)
                _commit(inventory, f"Removed {qty} from {target['ITEM']}.")


def render_idle_tab(inventory: Inventory) -> None:
    header("Idle Inventory Analysis", "🧠")

    idle_df = inventory.idle_inventory()
    if idle_df.empty:
        st.info("No idle inventory found.")
    else:
        st.dataframe(idle_df, width='stretch', hide_index=True)
