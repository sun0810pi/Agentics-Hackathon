import streamlit as st
from auth.cognito_client import get_cognito_client
from utils.validators import validate_email, validate_password
from utils.helpers import log_action
from config import config


def login_user(email: str, password: str, cognito) -> bool:
    result = cognito.login(email, password)
    if result['success']:
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.access_token = result.get('access_token', '')
        # Demo mode: get user info from config
        demo_user = config.DEMO_USERS.get(email, {})
        st.session_state.user_name = demo_user.get('name', email.split('@')[0].title())
        st.session_state.user_role = demo_user.get('role', 'viewer')
        return True
    return False


def login_page():
    IS_DARK = st.session_state.get('theme', 'dark') == 'dark'
    BG      = "#060912" if IS_DARK else "#f0f4ff"
    CARD_BG = "#0c1020" if IS_DARK else "#ffffff"
    BORDER  = "rgba(59,130,246,0.2)" if IS_DARK else "rgba(37,99,235,0.12)"
    TEXT    = "#e2e8f0" if IS_DARK else "#0f172a"
    TEXT2   = "#64748b"
    INPUT_BG= "#111827" if IS_DARK else "#f8faff"

    # Full page login CSS
    st.markdown(f"""<style>
    .main .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        background: {BG};
        min-height: 100vh;
    }}
    /* Login card centering */
    .login-wrap {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: {BG};
        padding: 2rem;
    }}
    .login-card {{
        width: 100%;
        max-width: 460px;
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 20px;
        padding: 2.5rem 2.25rem 2rem;
        box-shadow: 0 24px 64px rgba(0,0,0,0.4);
    }}
    .login-logo {{
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 20px rgba(59,130,246,0.6));
    }}
    .login-title {{
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }}
    .login-sub {{
        text-align: center;
        font-size: 0.78rem;
        color: {TEXT2};
        margin-bottom: 1.75rem;
        letter-spacing: 0.02em;
    }}
    /* Inputs override */
    .stTextInput > div > div > input {{
        background: {INPUT_BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        color: {TEXT} !important;
        padding: 0.65rem 0.9rem !important;
        font-size: 0.9rem !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }}
    .stTabs [data-testid="stTab"] {{
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }}
    /* Demo credential cards */
    .demo-card {{
        border-radius: 12px;
        padding: 0.85rem 0.75rem;
        text-align: center;
        cursor: pointer;
        transition: transform 0.15s;
    }}
    .demo-card:hover {{ transform: translateY(-2px); }}
    </style>""", unsafe_allow_html=True)

    # Center layout
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown(f"""
        <div class="login-logo">🛡️</div>
        <div class="login-title">{config.APP_NAME}</div>
        <div class="login-sub">{config.HACKATHON}</div>
        """, unsafe_allow_html=True)

        cognito = get_cognito_client()
        tab1, tab2 = st.tabs(["🔐  Login", "📝  Sign Up"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email address", placeholder="admin@agentflow.ai", key="login_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
                submitted = st.form_submit_button("🔐  Sign In", use_container_width=True, type="primary")

                if submitted:
                    if not email:
                        st.error("Please enter your email")
                    elif not password:
                        st.error("Please enter your password")
                    else:
                        with st.spinner("Signing in..."):
                            if login_user(email, password, cognito):
                                st.rerun()
                            else:
                                st.error("❌ Invalid email or password")

            # Demo credentials
            if config.get_demo_mode() == "demo" or not cognito.is_configured:
                st.markdown(f'<div style="text-align:center;color:{TEXT2};font-size:0.72rem;'
                           f'margin:1.25rem 0 0.6rem;font-weight:600;text-transform:uppercase;'
                           f'letter-spacing:.08em;">Demo Accounts</div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                accounts = [
                    (c1, "👑", "Admin", "admin@agentflow.ai", "Admin@2026!", "rgba(59,130,246,0.12)", "rgba(59,130,246,0.3)"),
                    (c2, "🔍", "Analyst", "analyst@agentflow.ai", "Analyst@2026!", "rgba(16,185,129,0.12)", "rgba(16,185,129,0.3)"),
                    (c3, "👤", "Viewer", "viewer@agentflow.ai", "Viewer@2026!", "rgba(245,158,11,0.12)", "rgba(245,158,11,0.3)"),
                ]
                for col, icon, role, mail, pwd, bg, bor in accounts:
                    with col:
                        st.markdown(f"""<div class="demo-card" style="background:{bg};border:1px solid {bor};">
                        <div style="font-size:1.4rem;">{icon}</div>
                        <div style="font-weight:700;font-size:0.82rem;color:{TEXT};margin:3px 0;">{role}</div>
                        <div style="font-size:0.68rem;color:{TEXT2};">{mail}</div>
                        <div style="font-size:0.68rem;color:{TEXT2};font-family:monospace;">{pwd}</div>
                        </div>""", unsafe_allow_html=True)

        with tab2:
            if not cognito.is_configured:
                st.info("Sign up not available in demo mode. Use a demo account above.")
            else:
                with st.form("signup_form", clear_on_submit=True):
                    name  = st.text_input("Full Name", placeholder="John Doe")
                    email = st.text_input("Email", placeholder="you@company.com")
                    pwd   = st.text_input("Password", type="password")
                    pwd2  = st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                        if pwd != pwd2:
                            st.error("Passwords don't match")
                        else:
                            st.info("Registration coming soon")
