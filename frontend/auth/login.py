import streamlit as st
from auth.cognito_client import get_cognito_client
from config import config


def login_user(email: str, password: str, cognito) -> bool:
    result = cognito.login(email, password)
    if result['success']:
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.access_token = result.get('access_token', '')
        demo = config.DEMO_USERS.get(email, {})
        st.session_state.user_name = demo.get('name', email.split('@')[0].title())
        st.session_state.user_role = demo.get('role', 'viewer')
        return True
    return False


def login_page():
    IS_DARK = st.session_state.get('theme', 'dark') == 'dark'
    BG      = "#060912" if IS_DARK else "#f0f4ff"
    BG2     = "#0c1020" if IS_DARK else "#ffffff"
    BOR     = "rgba(59,130,246,0.2)" if IS_DARK else "rgba(37,99,235,0.12)"
    TEXT    = "#f1f5f9" if IS_DARK else "#0f172a"
    TEXT2   = "#64748b"
    INP     = "#111827" if IS_DARK else "#f8faff"
    GR1     = "#3b82f6" if IS_DARK else "#2563eb"
    GR2     = "#06b6d4" if IS_DARK else "#0891b2"

    st.markdown(f"""<style>
    .main .block-container{{padding:0!important;max-width:100%!important;margin:0!important;}}
    .stApp>[data-testid="stAppViewContainer"]{{
        background:
            radial-gradient(ellipse 100% 70% at 20% -5%, rgba(59,130,246,0.12) 0%, transparent 55%),
            radial-gradient(ellipse 80% 60% at 80% 105%, rgba(6,182,212,0.09) 0%, transparent 50%),
            {BG} !important;
    }}
    /* Input styling */
    .stTextInput>div>div>input{{
        background:{INP}!important;border:1px solid {BOR}!important;
        border-radius:10px!important;color:{TEXT}!important;
        padding:0.75rem 1rem!important;font-size:0.9rem!important;
    }}
    .stTextInput>div>div>input:focus{{
        border-color:{GR1}!important;
        box-shadow:0 0 0 3px rgba(59,130,246,0.15)!important;
    }}
    .stTextInput label{{color:{TEXT2}!important;font-size:0.78rem!important;
        text-transform:uppercase!important;letter-spacing:.06em!important;font-weight:500!important;}}
    .stTabs [data-testid="stTab"]{{font-weight:600!important;font-size:0.9rem!important;}}
    .stButton>button[kind="primary"]{{
        background:linear-gradient(135deg,{GR1},{GR2})!important;
        border:none!important;color:#fff!important;font-weight:600!important;
        padding:0.75rem!important;font-size:0.95rem!important;
        border-radius:10px!important;
        box-shadow:0 4px 20px rgba(59,130,246,0.35)!important;
    }}
    .stButton>button[kind="primary"]:hover{{
        transform:translateY(-1px)!important;
        box-shadow:0 6px 24px rgba(59,130,246,0.45)!important;color:#fff!important;
    }}
    </style>""", unsafe_allow_html=True)

    # Centered layout
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        # Card
        st.markdown(f"""
<div style="background:{BG2};border:1px solid {BOR};border-radius:20px;
  padding:2.5rem 2rem 1.75rem;
  box-shadow:0 32px 80px rgba(0,0,0,{'0.5' if IS_DARK else '0.12'});
  margin-top:3rem;">
  <div style="text-align:center;margin-bottom:1.75rem;">
    <div style="font-size:3.5rem;filter:drop-shadow(0 0 24px rgba(59,130,246,0.6));
      margin-bottom:0.75rem;">🛡️</div>
    <div style="font-size:1.6rem;font-weight:700;letter-spacing:-.02em;
      background:linear-gradient(135deg,{GR1},{GR2});
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
      background-clip:text;">{config.APP_NAME}</div>
    <div style="font-size:0.8rem;color:{TEXT2};margin-top:4px;letter-spacing:.02em;">
      {config.HACKATHON}</div>
  </div>
</div>""", unsafe_allow_html=True)

        cognito = get_cognito_client()
        tab1, tab2 = st.tabs(["🔐  Sign In", "📝  Sign Up"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("Email address", placeholder="admin@agentflow.ai", key="l_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="l_pwd")
                st.markdown('<div style="height:0.25rem;"></div>', unsafe_allow_html=True)
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
                if submitted:
                    if not email: st.error("Enter your email")
                    elif not password: st.error("Enter your password")
                    else:
                        with st.spinner("Signing in..."):
                            if login_user(email, password, cognito): st.rerun()
                            else: st.error("❌ Invalid email or password")

            # Demo accounts
            if config.get_demo_mode() == "demo" or not cognito.is_configured:
                st.markdown(f"""<div style="text-align:center;color:{TEXT2};
                  font-size:0.7rem;font-weight:600;text-transform:uppercase;
                  letter-spacing:.1em;margin:1.5rem 0 0.75rem;">
                  ── Demo Accounts ──</div>""", unsafe_allow_html=True)

                accounts = [
                    ("👑","Admin","admin@agentflow.ai","Admin@2026!","rgba(59,130,246,0.1)","rgba(59,130,246,0.25)","#3b82f6"),
                    ("🔍","Analyst","analyst@agentflow.ai","Analyst@2026!","rgba(16,185,129,0.1)","rgba(16,185,129,0.25)","#10b981"),
                    ("👤","Viewer","viewer@agentflow.ai","Viewer@2026!","rgba(245,158,11,0.1)","rgba(245,158,11,0.25)","#f59e0b"),
                ]
                c1, c2, c3 = st.columns(3)
                for col, (icon, role, mail, pwd, bg, bor, clr) in zip([c1,c2,c3], accounts):
                    with col:
                        st.markdown(f"""<div style="background:{bg};border:1px solid {bor};
                          border-radius:12px;padding:1rem 0.75rem;text-align:center;">
                          <div style="font-size:1.6rem;">{icon}</div>
                          <div style="font-weight:700;font-size:0.82rem;color:{clr};margin:5px 0 3px;">{role}</div>
                          <div style="font-size:0.68rem;color:{TEXT2};">{mail}</div>
                          <div style="font-size:0.68rem;color:{TEXT2};font-family:monospace;margin-top:2px;">{pwd}</div>
                        </div>""", unsafe_allow_html=True)

        with tab2:
            if not cognito.is_configured:
                st.info("Sign up not available in demo mode.")
            else:
                with st.form("signup_form", clear_on_submit=True):
                    st.text_input("Full Name", placeholder="John Doe")
                    st.text_input("Email", placeholder="you@company.com")
                    st.text_input("Password", type="password")
                    st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                        st.info("Registration coming soon")
