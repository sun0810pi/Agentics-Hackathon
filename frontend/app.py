"""
app.py — AgentFlow Finance Guard
Entry point. Handles login only.
All pages render their own sidebar via components/sidebar.py
"""
import sys
import logging
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from config import config
from utils.helpers import init_session_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── MUST be first Streamlit call ──────────────────────────
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": f"{config.APP_NAME} v{config.APP_VERSION} — AI-Powered Invoice Fraud Detection",
    },
)

# ── Session defaults ───────────────────────────────────────
if "initialized" not in st.session_state:
    init_session_state({
        "logged_in": False,
        "user_email": "",
        "user_name": "",
        "user_role": "viewer",
        "access_token": "",
        "id_token": "",
        "refresh_token": "",
        "theme": "dark",
        "language": "EN",
        "initialized": True,
        "show_logout_confirm": False,
    })

# ── Theme ──────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_theme_css(theme: str) -> str:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    return DARK_THEME if theme == "dark" else LIGHT_THEME

def apply_theme():
    st.markdown(
        get_theme_css(st.session_state.get("theme", "dark")),
        unsafe_allow_html=True
    )

apply_theme()

# ── Main: show login page ──────────────────────────────────
def main():
    if st.session_state.get("logged_in", False):
        # Already logged in → go to Overview
        st.switch_page("pages/1_📊_Overview.py")
        return

    from auth.login import login_page
    login_page()

main()
