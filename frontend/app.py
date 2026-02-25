"""app.py — AgentFlow Finance Guard. Entry point / Login page."""
import sys
import logging
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from config import config
from utils.helpers import init_session_state

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{config.APP_NAME} v{config.APP_VERSION}"},
)

# Session defaults
if "initialized" not in st.session_state:
    init_session_state({
        "logged_in": False, "user_email": "", "user_name": "",
        "user_role": "viewer", "access_token": "", "id_token": "",
        "refresh_token": "", "theme": "dark", "language": "EN",
        "initialized": True, "show_logout_confirm": False,
    })

# Theme
@st.cache_data(show_spinner=False)
def get_theme_css(theme: str) -> str:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    return DARK_THEME if theme == "dark" else LIGHT_THEME

st.markdown(get_theme_css(st.session_state.get("theme", "dark")), unsafe_allow_html=True)

# Main
if st.session_state.get("logged_in", False):
    # Logged in at root URL → redirect to Overview
    st.switch_page("pages/1_Overview.py")
else:
    from auth.login import login_page
    login_page()
