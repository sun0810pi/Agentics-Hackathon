"""
app.py — AgentFlow Finance Guard
==================================
Entry point cho Streamlit Multipage App.

Kiến trúc:
  - app.py  = trang Home + sidebar dùng chung cho toàn app
  - pages/  = các trang con, Streamlit tự discover theo tên file

Sidebar (auth, theme, logout) được define ở đây và tự động
hiển thị trên TẤT CẢ các trang trong pages/.

Auth flow:
  - Chưa login → hiện login page (inline, không redirect)
  - Đã login   → hiện sidebar + render trang hiện tại
"""

import sys
import time
import logging
import importlib.util
from pathlib import Path
from typing import Callable

import streamlit as st

st.markdown("""
<style>
[data-testid="collapsedControl"],
button[kind="header"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    left: 0px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    z-index: 999999 !important;
    
    background: #4A9EFF !important;
    border: 3px solid white !important;
    border-left: none !important;
    border-radius: 0 20px 20px 0 !important;
    width: 50px !important;
    height: 80px !important;
    
    box-shadow: 4px 0 30px rgba(0,0,0,0.8) !important;
}

[data-testid="collapsedControl"]:hover {
    background: #00d4ff !important;
    width: 60px !important;
}

[data-testid="collapsedControl"] svg {
    fill: white !important;
    width: 28px !important;
    height: 28px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Add frontend root to sys.path ─────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME
from utils.helpers import init_session_state

# ── Logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ── Page config — PHẢI là lệnh Streamlit đầu tiên ─────────
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

# ── Page file map (key → actual filename trong pages/) ────
# Dùng key ngắn để routing, map sang tên file thực tế.
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

# Page metadata (title, icon, role access)
PAGE_META = {
    "overview":      {"title": "Overview",        "icon": "📊", "roles": ["admin", "analyst", "viewer"]},
    "upload":        {"title": "Upload Invoice",   "icon": "📄", "roles": ["admin", "analyst"]},
    "fraud":         {"title": "Fraud Detection",  "icon": "🚨", "roles": ["admin", "analyst"]},
    "ml_insights":   {"title": "ML Insights",      "icon": "🧠", "roles": ["admin", "analyst"]},
    "security":      {"title": "Security",         "icon": "🛡️", "roles": ["admin"]},
    "observability": {"title": "Observability",    "icon": "📈", "roles": ["admin", "analyst"]},
    "merchant":      {"title": "Merchant",         "icon": "💼", "roles": ["admin", "analyst", "viewer"]},
    "integrations":  {"title": "Integrations",     "icon": "🔗", "roles": ["admin"]},
    "settings":      {"title": "Settings",         "icon": "⚙️", "roles": ["admin", "analyst", "viewer"]},
}

# ── Session state defaults ─────────────────────────────────
if "initialized" not in st.session_state:
    init_session_state({
        "logged_in":           False,
        "user_email":          "",
        "user_name":           "",
        "user_role":           "viewer",
        "access_token":        "",
        "id_token":            "",
        "refresh_token":       "",
        "theme":               "dark",
        "language":            "EN",
        "current_page":        "overview",
        "initialized":         True,
        "show_logout_confirm": False,
    })
    logger.info("Session state initialized")


# ── Theme ──────────────────────────────────────────────────
@st.cache_data
def get_theme_css(theme: str) -> str:
    return DARK_THEME if theme == "dark" else LIGHT_THEME


def apply_theme():
    st.markdown(get_theme_css(st.session_state.get("theme", "dark")), unsafe_allow_html=True)


apply_theme()


# ── Auth helpers ───────────────────────────────────────────
def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def do_logout():
    """Clear session and run Cognito logout if token exists."""
    token = st.session_state.get("access_token", "")
    if token and token != "demo_access_token":
        try:
            from auth.cognito_client import get_cognito_client
            get_cognito_client().logout(token)
        except Exception:
            pass
    for key in ["logged_in", "user_email", "user_name", "user_role",
                "access_token", "id_token", "refresh_token"]:
        st.session_state[key] = "" if key != "logged_in" else False
    st.session_state.show_logout_confirm = False
    logger.info("User logged out")


# ── Dynamic page loader ────────────────────────────────────
def render_page(page_key: str):
    """
    Load và execute page file tương ứng với page_key.

    Dùng importlib để load file theo tên thực tế (1_📊_Overview.py...)
    thay vì import theo module name — fix lỗi PAGES_LOADED = False.
    """
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
        # Đưa vào sys.modules để tránh import vòng
        sys.modules[f"_agentflow_page_{page_key}"] = mod
        spec.loader.exec_module(mod)   # ← chạy top-level code của page file
    except Exception as e:
        logger.error(f"Error loading page {page_key}: {e}", exc_info=True)
        st.error(f"### ⚠️ Lỗi khi load trang **{page_key}**")
        st.error(f"**{type(e).__name__}:** {e}")
        with st.expander("🔍 Chi tiết lỗi"):
            st.exception(e)
        if st.button("🔄 Thử lại"):
            st.rerun()


# ── Sidebar ────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
            <div style='text-align:center; padding:1rem 0 2rem 0;'>
                <div style='font-size:3rem; margin-bottom:0.5rem;'>🛡️</div>
                <h1 style='margin:0; font-size:1.5rem;'>AgentFlow</h1>
                <p style='margin:0; opacity:0.7; font-size:0.875rem;'>Finance Guard</p>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # User info
        user_name  = st.session_state.get("user_name", "User")
        user_role  = st.session_state.get("user_role", "viewer").title()
        user_email = st.session_state.get("user_email", "")

        st.markdown(f"""
            <div style='padding:1rem; background:rgba(74,158,255,0.1); border-radius:12px; margin-bottom:1.5rem;'>
                <div style='font-weight:700; font-size:1rem;'>{user_name}</div>
                <div style='opacity:0.7; font-size:0.875rem;'>{user_role}</div>
                <div style='opacity:0.5; font-size:0.75rem; margin-top:0.25rem;'>{user_email}</div>
            </div>
        """, unsafe_allow_html=True)

        # Navigation — filter by role
        st.markdown("### 📋 Navigation")
        user_role_key  = st.session_state.get("user_role", "viewer").lower()
        current_page   = st.session_state.get("current_page", "overview")
        available_keys = [k for k, m in PAGE_META.items() if user_role_key in m["roles"]]

        try:
            current_index = available_keys.index(current_page)
        except ValueError:
            current_index = 0

        selected = st.radio(
            "Select page",
            options=available_keys,
            format_func=lambda k: f"{PAGE_META[k]['icon']} {PAGE_META[k]['title']}",
            index=current_index,
            label_visibility="collapsed",
            key="page_selector",
        )

        if selected != current_page:
            st.session_state.current_page = selected
            st.rerun()

        st.divider()

        # Theme toggle
        st.markdown("### 🎨 Theme")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "☀️ Light",
                use_container_width=True,
                type="primary" if st.session_state.theme == "light" else "secondary",
                key="theme_light",
            ):
                if st.session_state.theme != "light":
                    st.session_state.theme = "light"
                    st.rerun()
        with col2:
            if st.button(
                "🌙 Dark",
                use_container_width=True,
                type="primary" if st.session_state.theme == "dark" else "secondary",
                key="theme_dark",
            ):
                if st.session_state.theme != "dark":
                    st.session_state.theme = "dark"
                    st.rerun()

        st.divider()

        # Logout
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

        # Footer
        st.markdown(f"""
            <div style='margin-top:2rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.1);
                        text-align:center; opacity:0.5; font-size:0.75rem;'>
                AgentFlow v{config.APP_VERSION}<br/>© 2026 Anthropic
            </div>
        """, unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────
def main():
    if not is_logged_in():
        # Hiện login page inline (không cần switch_page)
        from auth.login import login_page
        login_page()
        return

    # Đã login → sidebar + render trang hiện tại
    render_sidebar()

    page_key  = st.session_state.get("current_page", "overview")
    user_role = st.session_state.get("user_role", "viewer").lower()
    meta      = PAGE_META.get(page_key, {})

    # Kiểm tra quyền truy cập
    if user_role not in meta.get("roles", []):
        st.warning(f"### 🔒 Access Denied")
        st.warning(f"Bạn không có quyền truy cập trang **{meta.get('title', page_key)}**")
        st.info(f"Cần role: {', '.join(meta.get('roles', []))}")
        st.info(f"Role hiện tại: **{user_role}**")
        return

    # Load và render page
    start = time.perf_counter()
    render_page(page_key)
    logger.debug(f"Page '{page_key}' rendered in {(time.perf_counter()-start)*1000:.1f}ms")


main()