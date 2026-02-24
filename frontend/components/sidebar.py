import streamlit as st
from typing import Optional, List, Dict, Any
from config import config
import logging

logger = logging.getLogger(__name__)


def render_sidebar(
    show_user_info: bool = True,
    show_theme_toggle: bool = True,
    show_logout: bool = True,
    custom_content: Optional[callable] = None
):
    """
    Render navigation sidebar with customizable sections
    
    Args:
        show_user_info: Display user information card
        show_theme_toggle: Display theme switcher
        show_logout: Display logout button
        custom_content: Optional function to render custom content
    """
    
    with st.sidebar:
        # Logo and branding
        _render_logo()
        
        st.divider()
        
        # User information
        if show_user_info:
            _render_user_info()
            st.divider()
        
        # Custom content (inserted here if provided)
        if custom_content:
            custom_content()
            st.divider()
        
        # Theme toggle
        if show_theme_toggle:
            _render_theme_toggle()
            st.divider()
        
        # Logout button
        if show_logout:
            _render_logout_button()
            st.divider()
        
        # Footer
        _render_footer()


def _render_logo():
    """Render app logo and title"""
    
    logo_html = """
        <div style='text-align: center; padding: 1rem 0 2rem 0;'>
            <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🛡️</div>
            <h1 style='margin: 0; font-size: 1.5rem; font-weight: 900; 
                       background: linear-gradient(135deg, #4A9EFF, #00d4ff, #a855f7);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       background-clip: text;'>
                AgentFlow
            </h1>
            <p style='margin: 0; opacity: 0.7; font-size: 0.875rem; font-weight: 600;'>
                Finance Guard
            </p>
        </div>
    """
    
    st.markdown(logo_html, unsafe_allow_html=True)


def _render_user_info():
    """Render user information card"""
    
    user_name = st.session_state.get('user_name', 'User')
    user_role = st.session_state.get('user_role', 'Viewer').title()
    user_email = st.session_state.get('user_email', '')
    
    # Role badge colors
    role_colors = {
        'Admin': '#4A9EFF',
        'Analyst': '#00d68f',
        'Viewer': '#ffab00'
    }
    
    role_color = role_colors.get(user_role, '#718096')
    
    user_card_html = f"""
        <div style='
            padding: 1rem;
            background: linear-gradient(135deg, rgba(74, 158, 255, 0.15), rgba(0, 212, 255, 0.05));
            border-radius: 12px;
            border: 1px solid rgba(74, 158, 255, 0.3);
            margin-bottom: 1rem;
        '>
            <div style='
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 0.75rem;
            '>
                <div style='
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #4A9EFF, #00d4ff);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    font-weight: 900;
                    color: white;
                '>
                    {user_name[0].upper()}
                </div>
                <div style='flex: 1;'>
                    <div style='font-weight: 700; font-size: 1rem; margin-bottom: 0.25rem;'>
                        {user_name}
                    </div>
                    <div style='
                        display: inline-block;
                        padding: 0.25rem 0.75rem;
                        background: {role_color}20;
                        border: 1px solid {role_color};
                        border-radius: 12px;
                        font-size: 0.75rem;
                        font-weight: 700;
                        color: {role_color};
                    '>
                        {user_role}
                    </div>
                </div>
            </div>
            <div style='
                opacity: 0.7;
                font-size: 0.75rem;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            '>
                {user_email}
            </div>
        </div>
    """
    
    st.markdown(user_card_html, unsafe_allow_html=True)


def _render_theme_toggle():
    """Render theme toggle buttons"""
    
    st.markdown("### 🎨 Theme")
    
    col1, col2 = st.columns(2)
    
    current_theme = st.session_state.get('theme', 'dark')
    
    with col1:
        light_type = "primary" if current_theme == 'light' else "secondary"
        if st.button(
            "☀️ Light",
            key="theme_light_sidebar",
            use_container_width=True,
            type=light_type
        ):
            if current_theme != 'light':
                st.session_state.theme = 'light'
                st.rerun()
    
    with col2:
        dark_type = "primary" if current_theme == 'dark' else "secondary"
        if st.button(
            "🌙 Dark",
            key="theme_dark_sidebar",
            use_container_width=True,
            type=dark_type
        ):
            if current_theme != 'dark':
                st.session_state.theme = 'dark'
                st.rerun()


def _render_logout_button():
    """Render logout button with confirmation"""
    
    # Check if confirmation is shown
    show_confirm = st.session_state.get('show_logout_confirm', False)
    
    if not show_confirm:
        if st.button(
            "🚪 Logout",
            key="logout_btn_sidebar",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.show_logout_confirm = True
            st.rerun()
    else:
        st.warning("⚠️ Logout?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Yes", key="logout_confirm_sidebar", use_container_width=True, type="primary"):
                from auth.login import logout
                logout()
                st.rerun()
        
        with col2:
            if st.button("❌ No", key="logout_cancel_sidebar", use_container_width=True):
                st.session_state.show_logout_confirm = False
                st.rerun()


def _render_footer():
    """Render sidebar footer"""
    
    footer_html = f"""
        <div style='
            margin-top: auto;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            opacity: 0.5;
            font-size: 0.75rem;
        '>
            <div style='margin-bottom: 0.5rem;'>
                AgentFlow v{config.APP_VERSION}
            </div>
            <div style='margin-bottom: 0.5rem;'>
                © 2026 Anthropic
            </div>
            <div style='font-size: 0.65rem;'>
                Built with ❤️ using Streamlit
            </div>
        </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)


def render_navigation_menu(pages: List[Dict[str, Any]]):
    """
    Render navigation menu for pages
    
    Args:
        pages: List of page dicts with 'key', 'title', 'icon'
    
    Example:
        pages = [
            {'key': 'overview', 'title': 'Overview', 'icon': '📊'},
            {'key': 'upload', 'title': 'Upload', 'icon': '📄'},
        ]
        render_navigation_menu(pages)
    """
    
    st.markdown("### 📋 Navigation")
    
    current_page = st.session_state.get('current_page', 'overview')
    
    # Filter by role
    user_role = st.session_state.get('user_role', 'viewer').lower()
    
    available_pages = [
        p for p in pages
        if user_role in p.get('roles', ['admin', 'analyst', 'viewer'])
    ]
    
    # Radio selection
    try:
        current_index = [p['key'] for p in available_pages].index(current_page)
    except ValueError:
        current_index = 0
    
    selected = st.radio(
        "Pages",
        options=[p['key'] for p in available_pages],
        format_func=lambda key: next(
            (f"{p['icon']} {p['title']}" for p in available_pages if p['key'] == key),
            key
        ),
        index=current_index,
        label_visibility="collapsed",
        key="page_selector_sidebar"
    )
    
    # Update if changed
    if selected != current_page:
        st.session_state.current_page = selected
        st.rerun()


def render_quick_stats(stats: List[Dict[str, Any]]):
    """
    Render quick stats in sidebar
    
    Args:
        stats: List of stat dicts with 'label', 'value', 'icon'
    
    Example:
        stats = [
            {'label': 'Active', 'value': '247', 'icon': '✅'},
            {'label': 'Pending', 'value': '12', 'icon': '⏳'},
        ]
        render_quick_stats(stats)
    """
    
    st.markdown("### 📊 Quick Stats")
    
    for stat in stats:
        label = stat.get('label', '')
        value = stat.get('value', '')
        icon = stat.get('icon', '📊')
        
        stat_html = f"""
            <div style='
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                margin-bottom: 0.5rem;
            '>
                <div style='font-size: 1.5rem;'>{icon}</div>
                <div style='flex: 1;'>
                    <div style='opacity: 0.7; font-size: 0.75rem;'>{label}</div>
                    <div style='font-weight: 700; font-size: 1.25rem;'>{value}</div>
                </div>
            </div>
        """
        
        st.markdown(stat_html, unsafe_allow_html=True)


def render_sidebar_alerts(alerts: List[Dict[str, Any]]):
    """
    Render alerts/notifications in sidebar
    
    Args:
        alerts: List of alert dicts with 'message', 'type', 'icon'
    """
    
    if not alerts:
        return
    
    st.markdown("### 🔔 Alerts")
    
    for alert in alerts:
        message = alert.get('message', '')
        alert_type = alert.get('type', 'info')
        icon = alert.get('icon', 'ℹ️')
        
        # Color based on type
        colors = {
            'info': '#4A9EFF',
            'success': '#00d68f',
            'warning': '#ffab00',
            'error': '#ff5252'
        }
        
        color = colors.get(alert_type, colors['info'])
        
        alert_html = f"""
            <div style='
                padding: 0.75rem;
                background: {color}20;
                border-left: 3px solid {color};
                border-radius: 6px;
                margin-bottom: 0.5rem;
                font-size: 0.875rem;
            '>
                <div style='display: flex; align-items: start; gap: 0.5rem;'>
                    <div>{icon}</div>
                    <div>{message}</div>
                </div>
            </div>
        """
        
        st.markdown(alert_html, unsafe_allow_html=True)


def render_sidebar_links(links: List[Dict[str, str]]):
    """
    Render useful links in sidebar
    
    Args:
        links: List of link dicts with 'text', 'url', 'icon'
    """
    
    st.markdown("### 🔗 Quick Links")
    
    for link in links:
        text = link.get('text', '')
        url = link.get('url', '#')
        icon = link.get('icon', '🔗')
        
        link_html = f"""
            <a href="{url}" target="_blank" style='
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 0.75rem;
                background: rgba(255,255,255,0.05);
                border-radius: 6px;
                margin-bottom: 0.5rem;
                text-decoration: none;
                color: inherit;
                transition: all 0.2s ease;
            '
            onmouseover="this.style.background='rgba(74, 158, 255, 0.2)'"
            onmouseout="this.style.background='rgba(255,255,255,0.05)'">
                <span>{icon}</span>
                <span style='font-size: 0.875rem;'>{text}</span>
            </a>
        """
        
        st.markdown(link_html, unsafe_allow_html=True)


# Convenience function for simple sidebar
def simple_sidebar():
    """Render simple sidebar with default options"""
    render_sidebar(
        show_user_info=True,
        show_theme_toggle=True,
        show_logout=True
    )


# Convenience function for custom sidebar
def custom_sidebar(
    user_info: bool = True,
    theme_toggle: bool = True,
    logout_button: bool = True,
    quick_stats: Optional[List[Dict]] = None,
    alerts: Optional[List[Dict]] = None,
    links: Optional[List[Dict]] = None
):
    """
    Render customizable sidebar with optional sections
    
    Args:
        user_info: Show user info card
        theme_toggle: Show theme toggle
        logout_button: Show logout button
        quick_stats: List of quick stats to display
        alerts: List of alerts to display
        links: List of links to display
    """
    
    with st.sidebar:
        _render_logo()
        st.divider()
        
        if user_info:
            _render_user_info()
            st.divider()
        
        if quick_stats:
            render_quick_stats(quick_stats)
            st.divider()
        
        if alerts:
            render_sidebar_alerts(alerts)
            st.divider()
        
        if links:
            render_sidebar_links(links)
            st.divider()
        
        if theme_toggle:
            _render_theme_toggle()
            st.divider()
        
        if logout_button:
            _render_logout_button()
            st.divider()
        
        _render_footer()