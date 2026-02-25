"""
app.py — AgentFlow Finance Guard
==================================
Entry point cho Streamlit Multipage App.
"""

import sys
import time
import logging
import importlib.util
from pathlib import Path

import streamlit as st

# ── Add frontend root to sys.path ─────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from utils.helpers import init_session_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ── set_page_config — PHẢI là lệnh Streamlit ĐẦU TIÊN ────
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help":    "https://github.com/yourusername/agentflow",
        "Report a bug":"https://github.com/yourusername/agentflow/issues",
        "About":       f"{config.APP_NAME} v{config.APP_VERSION} — AI-Powered Invoice Fraud Detection",
    },
)

PAGE_FILES = {
    "overview":      "1_📊_Overview.py",
    "upload":        "2_📄_Upload.py",
    "fraud":         "3_🚨_Fraud.py",
    "ml_insights":   "4_🧠_ML_Insights.py",
    "security":      "5_🛡️_Security.py",
    "observability": "6_📈_Observability.py",
    "merchant":      "7_💼_Merchant.py",
    "integrations":  "8_🔗_Integrations.py",
    "settings":      "9_⚙️_Settings.py",
}

PAGE_META = {
    "overview":      {"title": "Overview",       "icon": "📊", "roles": ["admin", "analyst", "viewer"]},
    "upload":        {"title": "Upload Invoice",  "icon": "📄", "roles": ["admin", "analyst"]},
    "fraud":         {"title": "Fraud Detection", "icon": "🚨", "roles": ["admin", "analyst"]},
    "ml_insights":   {"title": "ML Insights",     "icon": "🧠", "roles": ["admin", "analyst"]},
    "security":      {"title": "Security",        "icon": "🛡️", "roles": ["admin"]},
    "observability": {"title": "Observability",   "icon": "📈", "roles": ["admin", "analyst"]},
    "merchant":      {"title": "Merchant",        "icon": "💼", "roles": ["admin", "analyst", "viewer"]},
    "integrations":  {"title": "Integrations",    "icon": "🔗", "roles": ["admin"]},
    "settings":      {"title": "Settings",        "icon": "⚙️", "roles": ["admin", "analyst", "viewer"]},
}

if "initialized" not in st.session_state:
    init_session_state({
        "logged_in": False, "user_email": "", "user_name": "",
        "user_role": "viewer", "access_token": "", "id_token": "",
        "refresh_token": "", "theme": "dark", "language": "EN",
        "current_page": "overview", "initialized": True,
        "show_logout_confirm": False,
    })

@st.cache_data(show_spinner=False)
def get_theme_css(theme: str) -> str:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    return DARK_THEME if theme == "dark" else LIGHT_THEME

def apply_theme():
    st.markdown(get_theme_css(st.session_state.get("theme", "dark")), unsafe_allow_html=True)

apply_theme()

st.markdown("""
<style>
/* Sidebar toggle - override mọi thứ */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 999999 !important;
    position: fixed !important;
    left: 0 !important;
    top: 50vh !important;
    transform: translateY(-50%) !important;
    width: 40px !important;
    height: 60px !important;
    background: #4A9EFF !important;
    border-radius: 0 10px 10px 0 !important;
    border: none !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.4) !important;
    cursor: pointer !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="collapsedControl"]:hover {
    background: #2563eb !important;
    width: 46px !important;
}
[data-testid="collapsedControl"] svg {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    fill: white !important;
    color: white !important;
    stroke: white !important;
    width: 20px !important;
    height: 20px !important;
}
[data-testid="collapsedControl"] * {
    visibility: visible !important;
    color: white !important;
    fill: white !important;
    stroke: white !important;
    opacity: 1 !important;
    visibility: visible !important;
}
</style>
""", unsafe_allow_html=True)

def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)

def do_logout():
    token = st.session_state.get("access_token", "")
    if token and token != "demo_access_token":
        try:
            from auth.cognito_client import get_cognito_client
            get_cognito_client().logout(token)
        except Exception:
            pass
    for key in ["logged_in","user_email","user_name","user_role","access_token","id_token","refresh_token"]:
        st.session_state[key] = "" if key != "logged_in" else False
    st.session_state.show_logout_confirm = False

def render_page(page_key: str):
    filename = PAGE_FILES.get(page_key)
    if not filename:
        st.error(f"Page không tồn tại: {page_key}")
        return
    path = Path(__file__).parent / "pages" / filename
    if not path.exists():
        st.error(f"File không tồn tại: pages/{filename}")
        return
    try:
        spec = importlib.util.spec_from_file_location(page_key, str(path))
        mod  = importlib.util.module_from_spec(spec)
        sys.modules[f"_agentflow_page_{page_key}"] = mod
        spec.loader.exec_module(mod)
    except Exception as e:
        logger.error(f"Error loading page {page_key}: {e}", exc_info=True)
        st.error(f"### ⚠️ Lỗi khi load trang **{page_key}**")
        st.error(f"**{type(e).__name__}:** {e}")
        with st.expander("🔍 Chi tiết lỗi"):
            st.exception(e)
        if st.button("🔄 Thử lại"):
            st.rerun()

def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:1rem 0 2rem 0;">'
            '<div style="font-size:3rem;margin-bottom:0.5rem;">🛡️</div>'
            '<h1 style="margin:0;font-size:1.5rem;">AgentFlow</h1>'
            '<p style="margin:0;opacity:0.7;font-size:0.875rem;">Finance Guard</p>'
            '</div>', unsafe_allow_html=True)

        st.divider()

        user_name  = st.session_state.get("user_name", "User")
        user_role  = (st.session_state.get("user_role") or "viewer").title()
        user_email = st.session_state.get("user_email", "")

        st.markdown(
            f'<div style="padding:1rem;background:rgba(74,158,255,0.1);border-radius:12px;margin-bottom:1.5rem;">'
            f'<div style="font-weight:700;font-size:1rem;">{user_name}</div>'
            f'<div style="opacity:0.7;font-size:0.875rem;">{user_role}</div>'
            f'<div style="opacity:0.5;font-size:0.75rem;margin-top:0.25rem;">{user_email}</div>'
            f'</div>', unsafe_allow_html=True)

        st.markdown("### 📋 Navigation")
        user_role_key  = (st.session_state.get("user_role") or "viewer").lower()
        current_page   = st.session_state.get("current_page", "overview")
        available_keys = [k for k, m in PAGE_META.items() if user_role_key in m["roles"]]
        try:
            current_index = available_keys.index(current_page)
        except ValueError:
            current_index = 0

        selected = st.radio(
            "Select page", options=available_keys,
            format_func=lambda k: f"{PAGE_META[k]['icon']} {PAGE_META[k]['title']}",
            index=current_index, label_visibility="collapsed", key="page_selector",
        )
        if selected != current_page:
            st.session_state.current_page = selected
            st.rerun()

        st.divider()
        st.markdown("### 🎨 Theme")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("☀️ Light", use_container_width=True,
                         type="primary" if st.session_state.theme == "light" else "secondary",
                         key="theme_light"):
                if st.session_state.theme != "light":
                    st.session_state.theme = "light"
                    st.rerun()
        with col2:
            if st.button("🌙 Dark", use_container_width=True,
                         type="primary" if st.session_state.theme == "dark" else "secondary",
                         key="theme_dark"):
                if st.session_state.theme != "dark":
                    st.session_state.theme = "dark"
                    st.rerun()

        st.divider()
        if not st.session_state.get("show_logout_confirm", False):
            if st.button("🚪 Logout", use_container_width=True, type="secondary", key="logout_btn"):
                st.session_state.show_logout_confirm = True
                st.rerun()
        else:
            st.warning("⚠️ Are you sure you want to logout?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes", use_container_width=True, type="primary", key="logout_confirm"):
                    do_logout()
                    st.rerun()
            with c2:
                if st.button("❌ Cancel", use_container_width=True, key="logout_cancel"):
                    st.session_state.show_logout_confirm = False
                    st.rerun()

        st.markdown(
            f'<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.1);'
            f'text-align:center;opacity:0.5;font-size:0.75rem;">'
            f'AgentFlow v{config.APP_VERSION}<br/>© 2026 Anthropic</div>',
            unsafe_allow_html=True)

def main():
    if not is_logged_in():
        from auth.login import login_page
        login_page()
        return

    render_sidebar()

    page_key  = st.session_state.get("current_page", "overview")
    user_role = (st.session_state.get("user_role") or "viewer").lower()
    meta      = PAGE_META.get(page_key, {})

    if user_role not in meta.get("roles", []):
        st.warning("### 🔒 Access Denied")
        st.warning(f"Bạn không có quyền truy cập trang **{meta.get('title', page_key)}**")
        st.info(f"Cần role: {', '.join(meta.get('roles', []))}")
        st.info(f"Role hiện tại: **{user_role}**")
        return

    start = time.perf_counter()
    render_page(page_key)
    logger.debug(f"Page '{page_key}' rendered in {(time.perf_counter()-start)*1000:.1f}ms")

main()
