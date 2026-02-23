import streamlit as st
from auth.cognito_client import get_cognito_client
from utils.validators import validate_email, validate_password
from utils.helpers import log_action
from config import config


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'logged_in': False,
        'user_email': None,
        'user_name': None,
        'user_role': None,
        'access_token': None,
        'id_token': None,
        'refresh_token': None,
        'theme': 'dark',
        'language': 'EN'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(email: str, password: str, cognito: 'CognitoClient') -> bool:
    """
    Attempt to login user
    
    Args:
        email: User email
        password: User password
        cognito: Cognito client
        
    Returns:
        True if login successful
    """
    # Login via Cognito
    result = cognito.login(email, password)
    
    if result['success']:
        # Store tokens in session
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.access_token = result.get('access_token')
        st.session_state.id_token = result.get('id_token')
        st.session_state.refresh_token = result.get('refresh_token')
        
        # Get user info
        if result.get('access_token'):
            user_info = cognito.get_user_info(result['access_token'])
            if user_info.get('success'):
                st.session_state.user_name = user_info.get('name', email.split('@')[0])
        else:
            # Demo mode - get from demo users
            demo_user = config.DEMO_USERS.get(email, {})
            st.session_state.user_name = demo_user.get('name', email.split('@')[0])
            st.session_state.user_role = demo_user.get('role', 'user')
        
        # Log action
        log_action('login', {'email': email})
        
        return True
    else:
        return False


def logout_user():
    """Logout user and clear session"""
    email = st.session_state.get('user_email')
    
    # Logout via Cognito
    if st.session_state.get('access_token'):
        cognito = get_cognito_client()
        cognito.logout(st.session_state.access_token)
    
    # Log action
    log_action('logout', {'email': email})
    
    # Clear session
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.session_state.access_token = None
    st.session_state.id_token = None
    st.session_state.refresh_token = None


def login_page():
    """Render login page"""
    
    # Get Cognito client
    cognito = get_cognito_client()
    
    # Get translation
    lang = st.session_state.get('language', 'EN')
    t = config.TRANSLATIONS[lang]
    
    # Login container
    st.markdown(f"""
    <div class="login-container">
        <div class="login-logo">{config.APP_ICON}</div>
        <div class="login-title">{config.APP_NAME}</div>
        <div class="login-subtitle">{config.HACKATHON}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for login/signup
    tab1, tab2 = st.tabs([f"🔐 {t['login']}", f"📝 {t['signup']}"])
    
    # =====================================================
    # TAB 1: LOGIN
    # =====================================================
    with tab1:
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
                st.markdown(
                    f"<div style='text-align: right; padding-top: 5px;'>"
                    f"<a href='#' style='color: var(--primary);'>{t['forgot_password']}</a>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            submitted = st.form_submit_button(
                f"🔐 {t['login']}",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                # Validate inputs
                email_valid, email_error = validate_email(email)
                
                if not email:
                    st.error("❌ Please enter your email")
                elif not password:
                    st.error("❌ Please enter your password")
                elif not email_valid:
                    st.error(f"❌ {email_error}")
                else:
                    # Attempt login
                    with st.spinner("Logging in..."):
                        if login_user(email, password, cognito):
                            st.success("✅ Login successful!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
        
        # Demo credentials
        if config.get_demo_mode() == "demo" or not cognito.is_configured:
            with st.expander("🔑 Demo Credentials"):
                st.markdown("""
                **Demo accounts available:**
```
                Email: admin@agentflow.ai
                Password: Admin@2026!
                Role: Administrator
                
                Email: analyst@agentflow.ai
                Password: Analyst@2026!
                Role: Risk Analyst
                
                Email: viewer@agentflow.ai
                Password: Viewer@2026!
                Role: Viewer
```
                """)
    
    # =====================================================
    # TAB 2: SIGNUP
    # =====================================================
    with tab2:
        if not cognito.is_configured:
            st.warning("⚠️ Signup is not available in demo mode. Use demo accounts above.")
        else:
            with st.form("signup_form", clear_on_submit=False):
                signup_name = st.text_input(
                    "Full Name",
                    placeholder="John Doe",
                    key="signup_name"
                )
                
                signup_email = st.text_input(
                    t['email'],
                    placeholder="your.email@company.com",
                    key="signup_email"
                )
                
                signup_password = st.text_input(
                    t['password'],
                    type="password",
                    key="signup_password",
                    help="Min 8 chars, uppercase, lowercase, number, special character"
                )
                
                signup_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="signup_confirm"
                )
                
                submitted = st.form_submit_button(
                    f"📝 {t['signup']}",
                    use_container_width=True,
                    type="primary"
                )
                
                if submitted:
                    # Validate inputs
                    email_valid, email_error = validate_email(signup_email)
                    password_valid, password_error = validate_password(signup_password)
                    
                    if not signup_name:
                        st.error("❌ Please enter your name")
                    elif not email_valid:
                        st.error(f"❌ {email_error}")
                    elif not password_valid:
                        st.error(f"❌ {password_error}")
                    elif signup_password != signup_confirm:
                        st.error("❌ Passwords don't match")
                    else:
                        # Attempt signup
                        with st.spinner("Creating account..."):
                            result = cognito.signup(
                                signup_email,
                                signup_password,
                                signup_name
                            )
                            
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                st.info("💡 After verifying your email, return to the Login tab")
                            else:
                                st.error(f"❌ {result['error']}")
    
    # =====================================================
    # LANGUAGE SELECTOR
    # =====================================================
    st.markdown("---")
    st.markdown("### 🌐 Language / Ngôn ngữ")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.language = 'EN'
            st.rerun()
    with col2:
        if st.button("🇻🇳 Tiếng Việt", use_container_width=True):
            st.session_state.language = 'VI'
            st.rerun()
    
    # =====================================================
    # FOOTER
    # =====================================================
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: var(--text-secondary); font-size: 0.875rem;'>"
        f"© 2026 {config.APP_NAME} | {config.HACKATHON}"
        f"</div>",
        unsafe_allow_html=True
    )