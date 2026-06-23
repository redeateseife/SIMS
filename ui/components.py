# ui/components.py
#
# Renders UI elements using CSS classes defined in theme.py.
# No hardcoded colors, sizes, or font values here — all of that lives in TOKENS.

import streamlit as st

from ui.theme import TOKENS, stock_label
from services.inventory_service import Inventory
from services.backup_service import save_and_backup


# ==============================================================================
# HELPERS
# ==============================================================================

def html(content: str) -> None:
    st.markdown(content, unsafe_allow_html=True)


# ==============================================================================
# TYPOGRAPHY
# ==============================================================================

def page_title(text: str, subtitle: str = "") -> None:
    subtitle_html = f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    html(f'<div class="page-title">{text}</div>{subtitle_html}')


def header(title: str, icon: str = "") -> None:
    label = f"{icon} {title}" if icon else title
    html(f'<div class="section-header">{label}</div>')


# ==============================================================================
# METRICS
# ==============================================================================

def metric_row(total_items: int, stock: int, location: str) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 ITEMS",         total_items)
    c2.metric(stock_label(stock),  stock)
    c3.metric("📍 LOCATION",       location)


# ==============================================================================
# STATUS BADGE
# Reads colors from TOKENS so badge appearance is controlled by theme.py
# ==============================================================================

def badge(text: str, color: str = "info") -> None:
    color_map = {
        "success": token("color-success"),
        "warning": token("color-warning"),
        "danger":  token("color-danger"),
        "info":    token("color-info"),
    }
    bg = color_map.get(color, color)
    html(
        f'<span style="'
        f'background:{bg};'
        f'color:var(--badge-text-color);'
        f'padding:var(--badge-padding);'
        f'border-radius:var(--badge-radius);'
        f'font-size:var(--badge-size);'
        f'font-weight:var(--badge-weight);'
        f'">{text}</span>'
    )


# ==============================================================================
# DIVIDER
# ==============================================================================

def divider(color: str | None = None) -> None:
    border = color or "var(--divider-color)"
    html(f'<hr style="border:none;border-top:1px solid {border};margin:1rem 0;"/>')


# ==============================================================================
# SHUTDOWN SCREEN
# ==============================================================================

def shutdown_screen() -> None:
    st.components.v1.html(
        """
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;height:100vh;font-family:sans-serif;text-align:center;">
            <h1>SIMS Server Disconnected</h1>
            <p>You may close this browser tab.</p>
        </div>
        """,
        height=1000,
    )


# ==============================================================================
# TAB RENDERERS
# ==============================================================================

def _commit(inventory: Inventory, msg: str) -> None:
    """Persist changes, show feedback, and trigger a Streamlit rerun."""
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
    st.dataframe(display_df, width='stretch', hide_index=True)


def render_edit_tab(inventory: Inventory) -> None:
    col_add, col_remove = st.columns(2)

    with col_add:
        header("ADD / EDIT", "➕")

        with st.form("add_form", clear_on_submit=True):
            item_id  = st.number_input("ID",           min_value=1,  value=1000)
            item     = st.text_input("Item Name").strip().upper()
            qty      = st.number_input("Quantity",     min_value=1,  value=5)
            retail   = st.text_input("Retail Cost",    value="$1.00")
            sale     = st.text_input("Sale Price",     value="$2.50")
            location = st.text_input("Location Code").strip().upper()

            if st.form_submit_button("SAVE") and item and location:
                try:
                    inventory.add_or_edit(item_id, item, qty, retail, sale, location)
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
                inventory.remove(target["ID"], target["LOCATION"], qty)
                _commit(inventory, f"Removed {qty} from {target['ITEM']}.")


def render_idle_tab(inventory: Inventory) -> None:
    header("Idle Inventory Analysis", "🧠")

    idle_df = inventory.idle_inventory()
    if idle_df.empty:
        st.info("All items are isolated to unique locations.")
    else:
        st.dataframe(idle_df, width='stretch', hide_index=True)