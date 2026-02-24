import streamlit as st
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Any
import logging

# Add frontend to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from auth.login import show_login_page, is_logged_in, logout
from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME
from utils.helpers import init_session_state

# =====================================================
# IMPORT ALL PAGES AT MODULE LEVEL (NO DYNAMIC IMPORTS!)
# =====================================================
try:
    from pages import (
        page_overview,
        page_upload,
        page_fraud,
        page_ml_insights,
        page_security,
        page_observability,
        page_merchant,
        page_integrations,
        page_settings
    )
    PAGES_LOADED = True
except Exception as e:
    PAGES_LOADED = False
    PAGES_LOAD_ERROR = str(e)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================
# PAGE CONFIG - MUST BE FIRST STREAMLIT COMMAND
# =====================================================

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/agentflow',
        'Report a bug': 'https://github.com/yourusername/agentflow/issues',
        'About': f'{config.APP_NAME} v{config.APP_VERSION} - AI-Powered Invoice Fraud Detection'
    }
)

# =====================================================
# PAGE REGISTRY - CENTRALIZED CONFIGURATION
# =====================================================

class PageConfig:
    """Page configuration"""
    def __init__(
        self, 
        key: str, 
        title: str, 
        icon: str, 
        show_func: Callable,
        description: str = "",
        roles: list = None
    ):
        self.key = key
        self.title = title
        self.icon = icon
        self.show_func = show_func
        self.description = description
        self.roles = roles or ['admin', 'analyst', 'viewer']


# Define all pages with metadata
PAGES = [
    PageConfig(
        key='overview',
        title='Overview',
        icon='📊',
        show_func=page_overview.show if PAGES_LOADED else None,
        description='Dashboard overview with key metrics',
        roles=['admin', 'analyst', 'viewer']
    ),
    PageConfig(
        key='upload',
        title='Upload Invoice',
        icon='📄',
        show_func=page_upload.show if PAGES_LOADED else None,
        description='Upload and process invoices',
        roles=['admin', 'analyst']
    ),
    PageConfig(
        key='fraud',
        title='Fraud Detection',
        icon='🚨',
        show_func=page_fraud.show if PAGES_LOADED else None,
        description='Active fraud scenarios and alerts',
        roles=['admin', 'analyst']
    ),
    PageConfig(
        key='ml_insights',
        title='ML Insights',
        icon='🧠',
        show_func=page_ml_insights.show if PAGES_LOADED else None,
        description='Machine learning insights and analytics',
        roles=['admin', 'analyst']
    ),
    PageConfig(
        key='security',
        title='Security',
        icon='🛡️',
        show_func=page_security.show if PAGES_LOADED else None,
        description='Security monitoring and attack demos',
        roles=['admin']
    ),
    PageConfig(
        key='observability',
        title='Observability',
        icon='📈',
        show_func=page_observability.show if PAGES_LOADED else None,
        description='X-Ray traces and performance monitoring',
        roles=['admin', 'analyst']
    ),
    PageConfig(
        key='merchant',
        title='Merchant',
        icon='💼',
        show_func=page_merchant.show if PAGES_LOADED else None,
        description='Merchant insights and analytics',
        roles=['admin', 'analyst', 'viewer']
    ),
    PageConfig(
        key='integrations',
        title='Integrations',
        icon='🔗',
        show_func=page_integrations.show if PAGES_LOADED else None,
        description='External integrations and APIs',
        roles=['admin']
    ),
    PageConfig(
        key='settings',
        title='Settings',
        icon='⚙️',
        show_func=page_settings.show if PAGES_LOADED else None,
        description='User settings and preferences',
        roles=['admin', 'analyst', 'viewer']
    ),
]

# Create page lookup
PAGES_DICT = {p.key: p for p in PAGES}

# =====================================================
# INITIALIZE SESSION STATE (ONLY ONCE!)
# =====================================================

if 'initialized' not in st.session_state:
    init_session_state({
        'logged_in': False,
        'user_email': '',
        'user_name': '',
        'user_role': 'viewer',
        'access_token': '',
        'id_token': '',
        'refresh_token': '',
        'theme': 'dark',
        'language': 'EN',
        'current_page': 'overview',
        'initialized': True,
        'show_logout_confirm': False,
    })
    logger.info("Session state initialized")

# =====================================================
# APPLY THEME (CACHED)
# =====================================================

@st.cache_data
def get_theme_css(theme: str) -> str:
    """Get theme CSS (cached)"""
    return DARK_THEME if theme == 'dark' else LIGHT_THEME


def apply_theme():
    """Apply selected theme"""
    theme = st.session_state.get('theme', 'dark')
    theme_css = get_theme_css(theme)
    st.markdown(theme_css, unsafe_allow_html=True)


apply_theme()

# =====================================================
# ERROR BOUNDARY
# =====================================================

def with_error_boundary(func: Callable, *args, **kwargs):
    """
    Execute function with error boundary
    Prevents one page crash from crashing entire app
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
        
        st.error("### ⚠️ Oops! Something went wrong")
        st.error(f"**Error:** {str(e)}")
        
        with st.expander("🔍 Technical Details"):
            st.code(f"{type(e).__name__}: {str(e)}")
            st.text("Check logs for full traceback")
        
        if st.button("🔄 Refresh Page"):
            st.rerun()
        
        return None

# =====================================================
# SIDEBAR WITH NAVIGATION
# =====================================================

def render_sidebar():
    """Render sidebar with navigation and user info"""
    
    with st.sidebar:
        # Logo and title
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0 2rem 0;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🛡️</div>
                <h1 style='margin: 0; font-size: 1.5rem;'>AgentFlow</h1>
                <p style='margin: 0; opacity: 0.7; font-size: 0.875rem;'>Finance Guard</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # User info
        user_name = st.session_state.get('user_name', 'User')
        user_role = st.session_state.get('user_role', 'Viewer').title()
        user_email = st.session_state.get('user_email', '')
        
        st.markdown(f"""
            <div style='padding: 1rem; background: rgba(74, 158, 255, 0.1); border-radius: 12px; margin-bottom: 1.5rem;'>
                <div style='font-weight: 700; font-size: 1rem;'>{user_name}</div>
                <div style='opacity: 0.7; font-size: 0.875rem;'>{user_role}</div>
                <div style='opacity: 0.5; font-size: 0.75rem; margin-top: 0.25rem;'>{user_email}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("### 📋 Navigation")
        
        # Filter pages by role
        user_role_key = st.session_state.get('user_role', 'viewer').lower()
        available_pages = [p for p in PAGES if user_role_key in p.roles]
        
        # Use radio for navigation (better UX than buttons)
        current_page = st.session_state.get('current_page', 'overview')
        
        # Find current page index
        try:
            current_index = [p.key for p in available_pages].index(current_page)
        except ValueError:
            current_index = 0
        
        # Radio navigation
        selected = st.radio(
            "Select page",
            options=[p.key for p in available_pages],
            format_func=lambda key: f"{PAGES_DICT[key].icon} {PAGES_DICT[key].title}",
            index=current_index,
            label_visibility="collapsed",
            key="page_selector"
        )
        
        # Update current page if changed
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
                type="primary" if st.session_state.theme == 'light' else "secondary",
                key="theme_light"
            ):
                if st.session_state.theme != 'light':
                    st.session_state.theme = 'light'
                    st.rerun()
        
        with col2:
            if st.button(
                "🌙 Dark", 
                use_container_width=True, 
                type="primary" if st.session_state.theme == 'dark' else "secondary",
                key="theme_dark"
            ):
                if st.session_state.theme != 'dark':
                    st.session_state.theme = 'dark'
                    st.rerun()
        
        st.divider()
        
        # Logout button with confirmation
        if not st.session_state.get('show_logout_confirm', False):
            if st.button("🚪 Logout", use_container_width=True, type="secondary", key="logout_btn"):
                st.session_state.show_logout_confirm = True
                st.rerun()
        else:
            st.warning("⚠️ Are you sure you want to logout?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes", use_container_width=True, type="primary", key="logout_confirm"):
                    logout()
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True, key="logout_cancel"):
                    st.session_state.show_logout_confirm = False
                    st.rerun()
        
        # Footer
        st.markdown(f"""
            <div style='margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center; opacity: 0.5; font-size: 0.75rem;'>
                AgentFlow v{config.APP_VERSION}<br/>
                © 2026 Anthropic
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# RENDER CURRENT PAGE
# =====================================================

def render_current_page():
    """Render the current selected page with error boundary"""
    
    if not PAGES_LOADED:
        st.error("### ❌ Failed to load pages")
        st.error(f"**Error:** {PAGES_LOAD_ERROR}")
        st.info("Please check that all page files exist in the `pages/` directory")
        return
    
    current_page_key = st.session_state.get('current_page', 'overview')
    page_config = PAGES_DICT.get(current_page_key)
    
    if not page_config:
        st.error(f"Page not found: {current_page_key}")
        return
    
    # Check role access
    user_role = st.session_state.get('user_role', 'viewer').lower()
    if user_role not in page_config.roles:
        st.warning(f"### 🔒 Access Denied")
        st.warning(f"You don't have permission to access **{page_config.title}**")
        st.info(f"Required roles: {', '.join(page_config.roles)}")
        st.info(f"Your role: {user_role}")
        return
    
    # Show loading spinner
    with st.spinner(f"Loading {page_config.title}..."):
        # Performance monitoring
        start_time = time.time()
        
        # Render page with error boundary
        with_error_boundary(page_config.show_func)
        
        # Log render time
        render_time = (time.time() - start_time) * 1000
        logger.debug(f"Page {current_page_key} rendered in {render_time:.2f}ms")


# =====================================================
# MAIN APPLICATION
# =====================================================

def main():
    """Main application logic"""
    
    # Check authentication
    if not is_logged_in():
        with_error_boundary(show_login_page)
        return
    
    # User is logged in - show main app
    render_sidebar()
    render_current_page()


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    main()
