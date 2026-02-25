import streamlit as st
from typing import Optional, List, Dict, Any
from config import config
import logging

logger = logging.getLogger(__name__)

# Page definitions for navigation
PAGES = [
    {"title": "Overview",       "icon": "📊", "file": "pages/1_📊_Overview.py",       "roles": ["admin","analyst","viewer"]},
    {"title": "Upload Invoice", "icon": "📄", "file": "pages/2_📄_Upload.py",          "roles": ["admin","analyst"]},
    {"title": "Fraud",          "icon": "🚨", "file": "pages/3_🚨_Fraud.py",           "roles": ["admin","analyst"]},
    {"title": "ML Insights",    "icon": "🧠", "file": "pages/4_🧠_ML_Insights.py",     "roles": ["admin","analyst"]},
    {"title": "Security",       "icon": "🛡️", "file": "pages/5_🛡️_Security.py",       "roles": ["admin"]},
    {"title": "Observability",  "icon": "📈", "file": "pages/6_📈_Observability.py",   "roles": ["admin","analyst"]},
    {"title": "Merchant",       "icon": "💼", "file": "pages/7_💼_Merchant.py",        "roles": ["admin","analyst","viewer"]},
    {"title": "Integrations",   "icon": "🔗", "file": "pages/8_🔗_Integrations.py",   "roles": ["admin"]},
    {"title": "Settings",       "icon": "⚙️", "file": "pages/9_⚙️_Settings.py",       "roles": ["admin","analyst","viewer"]},
]


def render_sidebar():
    """Render full sidebar: logo + user info + navigation + theme + logout"""
    with st.sidebar:
        # ── Logo ──────────────────────────────────────────
        st.markdown(
            '<div style="text-align:center;padding:1rem 0 1.5rem 0;">'
            '<div style="font-size:3rem;margin-bottom:0.5rem;">🛡️</div>'
            '<h1 style="margin:0;font-size:1.5rem;font-weight:900;'
            'background:linear-gradient(135deg,#4A9EFF,#00d4ff);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
            'background-clip:text;">AgentFlow</h1>'
            '<p style="margin:0;opacity:0.7;font-size:0.875rem;">Finance Guard</p>'
            '</div>',
            unsafe_allow_html=True
        )

        st.divider()

        # ── User info ─────────────────────────────────────
        user_name  = st.session_state.get('user_name', 'User')
        user_role  = (st.session_state.get('user_role') or 'viewer').title()
        user_email = st.session_state.get('user_email', '')
        role_color = {'Admin':'#4A9EFF','Analyst':'#00d68f','Viewer':'#ffab00'}.get(user_role,'#718096')

        st.markdown(
            f'<div style="padding:0.75rem;background:rgba(74,158,255,0.1);'
            f'border-radius:12px;border:1px solid rgba(74,158,255,0.3);margin-bottom:1rem;">'
            f'<div style="font-weight:700;font-size:1rem;">{user_name}</div>'
            f'<div style="display:inline-block;padding:0.15rem 0.5rem;'
            f'background:{role_color}20;border:1px solid {role_color};border-radius:8px;'
            f'font-size:0.75rem;font-weight:700;color:{role_color};">{user_role}</div>'
            f'<div style="opacity:0.6;font-size:0.72rem;margin-top:0.25rem;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{user_email}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Navigation ────────────────────────────────────
        st.markdown("**📋 Navigation**")
        user_role_key = (st.session_state.get('user_role') or 'viewer').lower()

        for page in PAGES:
            if user_role_key in page['roles']:
                st.page_link(
                    page['file'],
                    label=f"{page['icon']} {page['title']}",
                    use_container_width=True,
                )

        st.divider()

        # ── Theme toggle ──────────────────────────────────
        st.markdown("**🎨 Theme**")
        col1, col2 = st.columns(2)
        cur = st.session_state.get('theme', 'dark')
        with col1:
            if st.button("☀️ Light", use_container_width=True,
                         type="primary" if cur=='light' else "secondary",
                         key="sb_theme_light"):
                if cur != 'light':
                    st.session_state.theme = 'light'
                    st.rerun()
        with col2:
            if st.button("🌙 Dark", use_container_width=True,
                         type="primary" if cur=='dark' else "secondary",
                         key="sb_theme_dark"):
                if cur != 'dark':
                    st.session_state.theme = 'dark'
                    st.rerun()

        st.divider()

        # ── Logout ────────────────────────────────────────
        if not st.session_state.get('show_logout_confirm', False):
            if st.button("🚪 Logout", use_container_width=True,
                         type="secondary", key="sb_logout"):
                st.session_state.show_logout_confirm = True
                st.rerun()
        else:
            st.warning("⚠️ Logout?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes", use_container_width=True,
                             type="primary", key="sb_logout_yes"):
                    from auth.login import logout
                    logout()
                    st.rerun()
            with c2:
                if st.button("❌ No", use_container_width=True, key="sb_logout_no"):
                    st.session_state.show_logout_confirm = False
                    st.rerun()

        # ── Footer ────────────────────────────────────────
        st.markdown(
            f'<div style="margin-top:1rem;padding-top:1rem;'
            f'border-top:1px solid rgba(255,255,255,0.1);'
            f'text-align:center;opacity:0.45;font-size:0.72rem;">'
            f'AgentFlow v{config.APP_VERSION}<br/>© 2026 Anthropic</div>',
            unsafe_allow_html=True
        )


# Keep old function names for backward compatibility
def render_navigation_menu(pages=None): pass
def render_quick_stats(stats=None): pass
def render_sidebar_alerts(alerts=None): pass
def render_sidebar_links(links=None): pass
def simple_sidebar(): render_sidebar()
def custom_sidebar(**kwargs): render_sidebar()
