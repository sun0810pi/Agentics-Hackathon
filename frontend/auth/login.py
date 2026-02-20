import streamlit as st
from config import config

def init_session_state():
    """Initialize all session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    if 'language' not in st.session_state:
        st.session_state.language = 'EN'
    if 'remember_me' not in st.session_state:
        st.session_state.remember_me = False

def login_user(email: str, password: str) -> bool:
    """Verify credentials and login"""
    user = config.DEMO_USERS.get(email)
    
    if user and user['password'] == password:
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.user_role = user['role']
        st.session_state.user_name = user['name']
        return True
    return False

def logout_user():
    """Logout and clear session"""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.session_state.user_name = None

def login_page():
    """Render login page"""
    
    # Language toggle
    lang = st.session_state.language
    t = config.TRANSLATIONS[lang]
    
    # Login container
    st.markdown(f"""
    <div class="login-container">
        <div class="login-logo">{config.APP_ICON}</div>
        <div class="login-title">{config.APP_NAME}</div>
        <div class="login-subtitle">{config.HACKATHON}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Form
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            t['email'],
            placeholder="admin@agentflow.ai",
            key="login_email"
        )
        
        password = st.text_input(
            t['password'],
            type="password",
            placeholder="••••••••",
            key="login_password"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember = st.checkbox(t['remember'], value=True)
        with col2:
            st.markdown(f"<div style='text-align: right; padding-top: 5px;'><a href='#' style='color: #4A9EFF;'>{t['forgot']}</a></div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button(f"🔐 {t['login']}", use_container_width=True, type="primary")
        
        if submitted:
            if login_user(email, password):
                st.session_state.remember_me = remember
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
    
    # Demo credentials
    with st.expander("🔑 Demo Credentials"):
        st.code("""
admin@agentflow.ai / admin123
analyst@agentflow.ai / analyst123
viewer@agentflow.ai / viewer123
        """)
    
    # Language selector
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.language = 'EN'
            st.rerun()
    with col2:
        if st.button("🇻🇳 Tiếng Việt", use_container_width=True):
            st.session_state.language = 'VI'
            st.rerun()