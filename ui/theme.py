# ui/theme.py
import streamlit as st

# ==============================================================================
# THEME TOKENS
# ==============================================================================
TOKENS = {
    # Layout Backgrounds
    "bg-app":              "#0B1220",   # Main page background
    "bg-surface":          "#111A2E",   # Cards, fields, sidebar panels
    
    # Text Roles
    "text-primary":        "#E6EDF7",   # Focus headers, titles, inputs
    "text-muted":          "#9AA7BD",   # Secondary text, labels, captions
    "text-inverse":        "#FFFFFF",   # Text on dark colored backgrounds
    "accent-orange":       "#FFA500",   # SIMS primary title accent

    # Global Specs
    "border-color":        "#22304A",   
    "border-radius":       "10px",      
    "space-sm":            "8px",
    "space-md":            "16px",

    # Status Semantic Colors
    "color-success":       "#22C55E",   # Green — Good stock
    "color-warning":       "#F59E0B",   # Amber — Low stock
    "color-danger":        "#EF4444",   # Red   — Empty stock
    "color-info":          "#3B82F6",   # Blue  — System info
}

# Font Sizing
SIZES = {
    "font-title":    "48px",
    "font-subtitle": "24px",
    "font-header":   "15px",
    "font-body":     "14px",
    "font-small":    "11px",
}

def var(name: str) -> str:
    return f"var(--{name})"

# ==============================================================================
# THEME INJECTION
# ==============================================================================
def apply_theme() -> None:
    css_vars = "\n        ".join(f"--{k}: {v};" for k, v in TOKENS.items())

    st.markdown(
        f"""
        <style>
        :root {{
            {css_vars}
        }}

        /* App Structural Backgrounds */
        .stApp {{ background-color: {var('bg-app')}; }}
        section[data-testid="stSidebar"] {{ background-color: {var('bg-surface')}; }}

        /* Typography Hierarchy */
        .page-title {{
            font-size: {SIZES['font-title']};
            color: {var('accent-orange')};
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 2px;
        }}
        .page-subtitle {{
            font-size: {SIZES['font-subtitle']};
            color: {var('text-muted')};
            font-weight: 400;
            margin-bottom: {var('space-md')};
            border-bottom: 2px solid #FFFF00;
            display: inline-block;
        }}
        .section-header, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
            font-size: {SIZES['font-header']} !important;
            color: {var('text-primary')} !important;
            font-weight: 700 !important;
            margin-bottom: {var('space-sm')};
        }}
        .stHeading h2, .stHeading h2 *, [data-testid="stHeading"] h2 {{
            color: {var('text-primary')} !important;
        }}

        /* UI Interactive Fields */
        label, .stSlider label, div[data-testid="stWidgetLabel"] p {{
            font-size: {SIZES['font-small']} !important;
            color: {var('text-muted')} !important;
            font-weight: 400 !important;
        }}
        input, textarea, div[data-baseweb="select"] {{
            font-size: {SIZES['font-body']} !important;
            color: {var('text-primary')} !important;
            background-color: {var('bg-surface')} !important;
            border-radius: {var('border-radius')} !important;
        }}

        /* Data Containers */
        div[data-testid="stMetric"] {{
            background-color: {var('bg-surface')};
            border: 1px solid {var('border-color')};
            border-radius: {var('border-radius')};
            padding: {var('space-md')};
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 26px !important;
            color: {var('text-primary')} !important;
            font-weight: 700 !important;
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: {SIZES['font-small']} !important;
            color: {var('text-muted')} !important;
            font-weight: 400 !important;
        }}
        div[data-testid="stDataFrame"] {{
            border-radius: {var('border-radius')};
            overflow: hidden;
        }}
        div[data-testid="stDataFrame"] * {{
            font-size: 13px !important;
            color: {var('text-primary')} !important;
        }}

        /* Callouts & Actions */
        .stCaption, caption, small {{
            font-size: {SIZES['font-small']} !important;
            color: {var('text-muted')} !important;
        }}
        button[data-testid^="stBaseButton"] {{
            font-size: 13px !important;
            color: {var('text-inverse')} !important;
            font-weight: 700 !important;
            background-color: {var('color-info')} !important; /* Default blue action */
            border-radius: {var('border-radius')} !important;
            border: none !important;
            transition: opacity 0.15s ease;
        }}
        button:hover {{ opacity: 0.85; }}

        div[data-testid="stTabs"] button {{
            font-size: {SIZES['font-header']} !important;
            color: {var('text-muted')} !important;
            background-color: transparent !important;
        }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: {var('text-primary')} !important;
            border-bottom: 2px solid var(--color-info) !important;
        }}
        div[data-testid="stAlert"] {{ border-radius: {var('border-radius')} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# STOCK LEVEL SYSTEM
# ==============================================================================
def _stock_tier(value: int):
    if value <= 0:
        return "🔴 STOCK", "color-danger"
    if value <= 10:
        return "🟠 STOCK", "color-warning"
    return "🟢 STOCK", "color-success"

def stock_label(value: int) -> str:
    return _stock_tier(value)[0]

def stock_color(value: int) -> str:
    return TOKENS[_stock_tier(value)[1]]
