# app.py — SIMS (Smart Inventory Management System)
# SINCE 2026-05-29

# app.py is intentionally thin: it owns page config, session state, the sidebar,
# and tab layout only. Rendering logic lives in ui/components.py.

import streamlit as st

from services.inventory_service import Inventory
from utils.system_utils import shutdown_server
from ui.components import (
    shutdown_screen,
    render_view_tab,
    render_edit_tab,
    render_idle_tab,
)

# =============================================================================
# PAGE CONFIG 
# =============================================================================
st.set_page_config(
    page_title="SIMS",
    page_icon="📦",
    layout="wide"
)

# =============================================================================
# SESSION STATE
# Storing Inventory in session_state so CSV is read once per browser
# session rather than on every widget interaction
# =============================================================================
if "inventory" not in st.session_state:
    st.session_state.inventory = Inventory()

inventory: Inventory = st.session_state.inventory

# =============================================================================
# PAGE TITLE
# =============================================================================
st.title("📦 SIMS")
st.caption("Smart Inventory Management System")

# =============================================================================
# SIDEBAR
# =============================================================================
if st.sidebar.button("EXIT"):
    st.sidebar.warning("Shutting down backend...")
    shutdown_screen()
    shutdown_server()

st.sidebar.header("FILTER")
selected_location = st.sidebar.selectbox(
    "LOCATION",
    ["ALL"] + inventory.locations(),
)

# =============================================================================
# TABS
# =============================================================================
view_tab, edit_tab, idle_tab = st.tabs(["VIEW", "EDIT", "IDLE"])

with view_tab:
    render_view_tab(inventory, selected_location)

with edit_tab:
    render_edit_tab(inventory)

with idle_tab:
    render_idle_tab(inventory)
