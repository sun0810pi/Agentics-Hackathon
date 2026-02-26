"""app.py — AgentFlow Finance Guard. Entry point / Login page."""
import sys, logging
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import config
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title=config.APP_NAME, page_icon="🛡️", layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{config.APP_NAME} v{config.APP_VERSION}"},
)

# Session defaults
_D = {"logged_in":False,"user_email":"","user_name":"","user_role":"viewer",
      "access_token":"","theme":"dark","initialized":True,"show_logout_confirm":False}
for k,v in _D.items():
    if k not in st.session_state: st.session_state[k] = v

# Theme
try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    st.markdown(DARK_THEME if st.session_state.theme=="dark" else LIGHT_THEME, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Theme error: {e}")

# Main
if st.session_state.get("logged_in"):
    try:
        from components.sidebar import render_sidebar
        render_sidebar()
    except Exception as e:
        st.sidebar.error(f"Sidebar: {e}")
    
    st.title(f"👋 Welcome, {st.session_state.get('user_name','User')}!")
    st.markdown(
        '<a href="/Overview" target="_self">'
        '<button style="margin-top:1rem;padding:0.75rem 2rem;background:#4A9EFF;'
        'color:white;border:none;border-radius:10px;cursor:pointer;font-size:1rem;font-weight:700;">'
        '📊 Go to Dashboard →</button></a>',
        unsafe_allow_html=True
    )
else:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback
        st.error(f"Login error: {e}")
        st.code(traceback.format_exc())
