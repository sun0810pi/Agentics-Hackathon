import streamlit as st
from config import config

PAGES = [
    {"title": "Overview",       "icon": "📊", "url": "/Overview",      "file": "pages/1_📊_Overview.py",     "roles": ["admin","analyst","viewer"]},
    {"title": "Upload Invoice", "icon": "📄", "url": "/Upload",        "file": "pages/2_📄_Upload.py",        "roles": ["admin","analyst"]},
    {"title": "Fraud",          "icon": "🚨", "url": "/Fraud",         "file": "pages/3_🚨_Fraud.py",         "roles": ["admin","analyst"]},
    {"title": "ML Insights",    "icon": "🧠", "url": "/ML_Insights",   "file": "pages/4_🧠_ML_Insights.py",   "roles": ["admin","analyst"]},
    {"title": "Security",       "icon": "🛡️", "url": "/Security",      "file": "pages/5_🛡️_Security.py",     "roles": ["admin"]},
    {"title": "Observability",  "icon": "📈", "url": "/Observability", "file": "pages/6_📈_Observability.py", "roles": ["admin","analyst"]},
    {"title": "Merchant",       "icon": "💼", "url": "/Merchant",      "file": "pages/7_💼_Merchant.py",      "roles": ["admin","analyst","viewer"]},
    {"title": "Integrations",   "icon": "🔗", "url": "/Integrations",  "file": "pages/8_🔗_Integrations.py",  "roles": ["admin"]},
    {"title": "Settings",       "icon": "⚙️", "url": "/Settings",      "file": "pages/9_⚙️_Settings.py",     "roles": ["admin","analyst","viewer"]},
]


def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown(
            '<div style="text-align:center;padding:1rem 0 1.5rem;">'
            '<div style="font-size:3rem;">🛡️</div>'
            '<h1 style="margin:0;font-size:1.4rem;font-weight:900;color:#4A9EFF;">AgentFlow</h1>'
            '<p style="margin:0;opacity:0.6;font-size:0.85rem;">Finance Guard</p>'
            '</div>',
            unsafe_allow_html=True
        )
        st.divider()

        # User info
        user_name  = st.session_state.get('user_name', 'User')
        user_role  = (st.session_state.get('user_role') or 'viewer').title()
        user_email = st.session_state.get('user_email', '')
        role_color = {'Admin':'#4A9EFF','Analyst':'#00d68f','Viewer':'#ffab00'}.get(user_role,'#718096')

        st.markdown(
            f'<div style="padding:0.75rem;background:rgba(74,158,255,0.1);border-radius:10px;'
            f'border:1px solid rgba(74,158,255,0.25);margin-bottom:0.75rem;">'
            f'<div style="font-weight:700;">{user_name}</div>'
            f'<span style="padding:0.1rem 0.5rem;background:{role_color}25;border:1px solid {role_color};'
            f'border-radius:6px;font-size:0.72rem;font-weight:700;color:{role_color};">{user_role}</span>'
            f'<div style="opacity:0.55;font-size:0.72rem;margin-top:0.3rem;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{user_email}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Navigation using buttons + switch_page
        st.markdown("**📋 Navigation**")
        user_role_key = (st.session_state.get('user_role') or 'viewer').lower()
        
        # Detect current page from URL
        try:
            current_url = st.context.url_path if hasattr(st, 'context') else ''
        except Exception:
            current_url = ''

        for page in PAGES:
            if user_role_key not in page['roles']:
                continue
            
            is_current = page['url'].lstrip('/').lower() in current_url.lower()
            btn_type = "primary" if is_current else "secondary"
            
            if st.button(
                f"{page['icon']} {page['title']}",
                key=f"nav_{page['title']}",
                use_container_width=True,
                type=btn_type,
            ):
                st.switch_page(page['file'])

        st.divider()

        # Theme toggle
        st.markdown("**🎨 Theme**")
        cur = st.session_state.get('theme', 'dark')
        col1, col2 = st.columns(2)
        with col1:
            if st.button("☀️ Light", use_container_width=True,
                         type="primary" if cur=='light' else "secondary",
                         key="sb_theme_light"):
                st.session_state.theme = 'light'
                st.rerun()
        with col2:
            if st.button("🌙 Dark", use_container_width=True,
                         type="primary" if cur=='dark' else "secondary",
                         key="sb_theme_dark"):
                st.session_state.theme = 'dark'
                st.rerun()

        st.divider()

        # Logout
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
                    st.switch_page("app.py")
            with c2:
                if st.button("❌ No", use_container_width=True, key="sb_logout_no"):
                    st.session_state.show_logout_confirm = False
                    st.rerun()

        st.markdown(
            f'<div style="margin-top:1rem;padding-top:0.75rem;border-top:1px solid rgba(255,255,255,0.1);'
            f'text-align:center;opacity:0.4;font-size:0.7rem;">'
            f'AgentFlow v{config.APP_VERSION} • © 2026</div>',
            unsafe_allow_html=True
        )


# Backward compat stubs
def render_navigation_menu(pages=None): pass
def render_quick_stats(stats=None): pass
def render_sidebar_alerts(alerts=None): pass
def render_sidebar_links(links=None): pass
def simple_sidebar(): render_sidebar()
def custom_sidebar(**kwargs): render_sidebar()
