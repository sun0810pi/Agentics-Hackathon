import streamlit as st
from config import config
import traceback

PAGES = [
    {"title": "Overview",       "icon": "📊", "url": "/Overview",      "roles": ["admin","analyst","viewer"]},
    {"title": "Upload",         "icon": "📄", "url": "/Upload",        "roles": ["admin","analyst"]},
    {"title": "Fraud",          "icon": "🚨", "url": "/Fraud",         "roles": ["admin","analyst"]},
    {"title": "ML Insights",    "icon": "🧠", "url": "/ML_Insights",   "roles": ["admin","analyst"]},
    {"title": "Security",       "icon": "🛡️", "url": "/Security",      "roles": ["admin"]},
    {"title": "Observability",  "icon": "📈", "url": "/Observability", "roles": ["admin","analyst"]},
    {"title": "Merchant",       "icon": "💼", "url": "/Merchant",      "roles": ["admin","analyst","viewer"]},
    {"title": "Integrations",   "icon": "🔗", "url": "/Integrations",  "roles": ["admin"]},
    {"title": "Settings",       "icon": "⚙️", "url": "/Settings",      "roles": ["admin","analyst","viewer"]},
]


def render_sidebar():
    try:
        _render_sidebar_inner()
    except Exception as e:
        # Never let sidebar crash kill the page
        st.sidebar.error(f"Sidebar error: {e}")


def _render_sidebar_inner():
    with st.sidebar:
        # Logo
        st.markdown(
            '<div style="text-align:center;padding:1rem 0 1rem;">'
            '<div style="font-size:2.5rem;">🛡️</div>'
            '<div style="font-size:1.3rem;font-weight:900;color:#4A9EFF;">AgentFlow</div>'
            '<div style="opacity:0.6;font-size:0.8rem;">Finance Guard</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.divider()

        # User info
        user_name  = st.session_state.get('user_name', 'User')
        user_role  = (st.session_state.get('user_role') or 'viewer').title()
        user_email = st.session_state.get('user_email', '')
        rc = {'Admin':'#4A9EFF','Analyst':'#00d68f','Viewer':'#ffab00'}.get(user_role,'#718096')
        st.markdown(
            f'<div style="padding:0.6rem;background:rgba(74,158,255,0.1);border-radius:8px;' f'border:1px solid rgba(74,158,255,0.2);margin-bottom:0.5rem;">'
            f'<b>{user_name}</b><br/>'
            f'<span style="font-size:0.72rem;color:{rc};font-weight:700;">{user_role}</span><br/>'
            f'<span style="font-size:0.68rem;opacity:0.55;">{user_email}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Navigation — HTML anchor links (most reliable, no switch_page emoji issues)
        st.markdown("**📋 Navigation**")
        user_role_key = (st.session_state.get('user_role') or 'viewer').lower()
        
        nav_links = ''
        for page in PAGES:
            if user_role_key not in page['roles']:
                continue
            nav_links += (
                f'<a href="{page["url"]}" target="_self" style="' f'display:block;padding:0.5rem 0.75rem;margin:0.2rem 0;' f'border-radius:8px;text-decoration:none;color:inherit;' f'background:rgba(255,255,255,0.05);' f'border:1px solid rgba(255,255,255,0.08);' f'font-size:0.9rem;font-weight:500;' f'transition:background 0.2s;"'
                f' onmouseover="this.style.background=\'rgba(74,158,255,0.2)\'"'
                f' onmouseout="this.style.background=\'rgba(255,255,255,0.05)\'">'
                f'{page["icon"]} {page["title"]}</a>'
            )
        
        st.markdown(nav_links, unsafe_allow_html=True)
        st.divider()

        # Theme toggle
        st.markdown("**🎨 Theme**")
        cur = st.session_state.get('theme', 'dark')
        col1, col2 = st.columns(2)
        with col1:
            if st.button("☀️ Light", use_container_width=True,
                         type="primary" if cur=='light' else "secondary",
                         key="sb_light"):
                st.session_state.theme = 'light'
                st.rerun()
        with col2:
            if st.button("🌙 Dark", use_container_width=True,
                         type="primary" if cur=='dark' else "secondary",
                         key="sb_dark"):
                st.session_state.theme = 'dark'
                st.rerun()

        st.divider()

        # Logout
        if not st.session_state.get('show_logout_confirm', False):
            if st.button("🚪 Logout", use_container_width=True, type="secondary", key="sb_logout"):
                st.session_state.show_logout_confirm = True
                st.rerun()
        else:
            st.warning("⚠️ Logout?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes", use_container_width=True, type="primary", key="sb_yes"):
                    for k in ['logged_in','user_email','user_name','user_role','access_token']:
                        st.session_state[k] = False if k == 'logged_in' else ''
                    st.session_state.show_logout_confirm = False
                    st.switch_page("app.py")
            with c2:
                if st.button("❌ No", use_container_width=True, key="sb_no"):
                    st.session_state.show_logout_confirm = False
                    st.rerun()

        st.markdown(
            f'<div style="text-align:center;opacity:0.35;font-size:0.68rem;padding-top:0.5rem;">'
            f'AgentFlow v{config.APP_VERSION}</div>',
            unsafe_allow_html=True
        )


# Backward compat stubs
def render_navigation_menu(pages=None): pass
def render_quick_stats(stats=None): pass
def render_sidebar_alerts(alerts=None): pass
def render_sidebar_links(links=None): pass
def simple_sidebar(): render_sidebar()
def custom_sidebar(**kwargs): render_sidebar()
