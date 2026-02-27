import streamlit as st
from auth.cognito_client import get_cognito_client
from config import config


def login_user(email: str, password: str, cognito) -> bool:
    result = cognito.login(email, password)
    if result['success']:
        st.session_state.logged_in   = True
        st.session_state.user_email  = email
        st.session_state.access_token = result.get('access_token', '')
        demo = config.DEMO_USERS.get(email, {})
        st.session_state.user_name = demo.get('name', email.split('@')[0].title())
        st.session_state.user_role = demo.get('role', 'viewer')
        return True
    return False


def logout():
    """
    Logout user and clear session state
    """
    for key in ["logged_in", "user_email", "user_name", "user_role", "access_token"]:
        st.session_state[key] = False if key == "logged_in" else ""
    st.session_state.page = "Overview"


def login_page():
    IS_DARK = st.session_state.get('theme', 'dark') == 'dark'
    CARD    = "#0b101e" if IS_DARK else "#ffffff"
    BOR     = "rgba(59,130,246,0.25)" if IS_DARK else "rgba(37,99,235,0.15)"
    TEXT    = "#f1f5f9" if IS_DARK else "#0f172a"
    TEXT2   = "#64748b"
    INP     = "#111827" if IS_DARK else "#f8faff"
    GR1, GR2 = ("#3b82f6","#06b6d4") if IS_DARK else ("#2563eb","#0891b2")

    # CSS only — no raw HTML divs outside <style>
    st.markdown(f"""<style>
    .main .block-container{{padding:0!important;max-width:100%!important;margin:0!important;}}

    /* Inputs */
    .stTextInput>div>div>input{{
        background:{INP}!important;border:1px solid {BOR}!important;
        border-radius:10px!important;color:{TEXT}!important;
        padding:.75rem 1rem!important;font-size:.9rem!important;
        transition:border-color .2s,box-shadow .2s!important;
    }}
    .stTextInput>div>div>input:focus{{
        border-color:{GR1}!important;box-shadow:0 0 0 3px rgba(59,130,246,.15)!important;
    }}
    .stTextInput label{{
        color:{TEXT2}!important;font-size:.75rem!important;
        text-transform:uppercase!important;letter-spacing:.07em!important;font-weight:600!important;
    }}

    /* Sign in button */
    .stButton>button[kind="primary"]{{
        background:linear-gradient(135deg,{GR1},{GR2})!important;
        border:none!important;color:#fff!important;font-weight:600!important;
        padding:.75rem!important;font-size:.95rem!important;border-radius:10px!important;
        box-shadow:0 4px 24px rgba(59,130,246,.4)!important;transition:all .2s!important;
    }}
    .stButton>button[kind="primary"]:hover{{
        transform:translateY(-2px)!important;
        box-shadow:0 8px 32px rgba(59,130,246,.55)!important;color:#fff!important;
    }}

    /* Tabs */
    [data-testid="stTabs"]{{border-bottom:1px solid {BOR}!important;margin-bottom:.5rem!important;}}
    [data-testid="stTabs"] button{{
        color:{TEXT2}!important;font-weight:600!important;font-size:.875rem!important;padding:.65rem 1.25rem!important;
    }}
    [data-testid="stTabs"] button[aria-selected="true"]{{
        color:{GR1}!important;border-bottom:2px solid {GR1}!important;
    }}

    /* Demo cards */
    .demo-card{{
        border-radius:12px;padding:.9rem .75rem;text-align:center;
    }}
    </style>""", unsafe_allow_html=True)

    # Full-page centering via Streamlit columns (no raw HTML wrapper)
    _, mid, _ = st.columns([1, 1.15, 1])
    with mid:
        # Hero card via markdown
        st.markdown(f"""
<div style="background:{CARD};border:1px solid {BOR};border-radius:22px;
  padding:2.5rem 2rem 1.75rem;margin-top:2rem;
  box-shadow:0 40px 100px rgba(0,0,0,{'0.55' if IS_DARK else '0.1'}),
             0 0 0 1px rgba(59,130,246,0.06);">
  <div style="text-align:center;margin-bottom:1.75rem;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
      width:68px;height:68px;border-radius:16px;
      background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(6,182,212,0.1));
      border:1px solid rgba(59,130,246,0.25);margin-bottom:.875rem;
      box-shadow:0 0 40px rgba(59,130,246,0.2);font-size:2rem;">🛡️</div>
    <div style="font-size:1.55rem;font-weight:700;letter-spacing:-.025em;
      background:linear-gradient(135deg,{GR1},{GR2});
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      {config.APP_NAME}</div>
    <div style="font-size:.78rem;color:{TEXT2};margin-top:4px;letter-spacing:.03em;">
      {config.HACKATHON}</div>
  </div>
</div>""", unsafe_allow_html=True)

        cognito = get_cognito_client()
        tab1, tab2 = st.tabs(["🔐  Sign In", "📝  Sign Up"])

        with tab1:
            st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)
            # Form NOT inside any sub-column to avoid Streamlit submit button bug
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("Email address", placeholder="admin@agentflow.ai")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                st.markdown('<div style="height:.2rem"></div>', unsafe_allow_html=True)
                submitted = st.form_submit_button("Sign In  →", use_container_width=True, type="primary")
                if submitted:
                    if not email:    st.error("Enter your email")
                    elif not password: st.error("Enter your password")
                    else:
                        with st.spinner("Signing in..."):
                            if login_user(email, password, cognito): st.rerun()
                            else: st.error("❌ Invalid credentials")

            # Demo accounts section
            if config.get_demo_mode() == "demo" or not cognito.is_configured:
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:.6rem;margin:1.4rem 0 .9rem;">
  <div style="flex:1;height:1px;background:{'rgba(255,255,255,0.07)' if IS_DARK else 'rgba(0,0,0,0.07)'}"></div>
  <span style="font-size:.65rem;color:{TEXT2};font-weight:600;text-transform:uppercase;letter-spacing:.1em;">Demo Accounts</span>
  <div style="flex:1;height:1px;background:{'rgba(255,255,255,0.07)' if IS_DARK else 'rgba(0,0,0,0.07)'}"></div>
</div>""", unsafe_allow_html=True)

                accounts = [
                    ("👑","Admin","admin@agentflow.ai","Admin@2026!","rgba(59,130,246,0.1)","rgba(59,130,246,0.22)","#60a5fa"),
                    ("🔍","Analyst","analyst@agentflow.ai","Analyst@2026!","rgba(16,185,129,0.1)","rgba(16,185,129,0.22)","#34d399"),
                    ("👤","Viewer","viewer@agentflow.ai","Viewer@2026!","rgba(245,158,11,0.1)","rgba(245,158,11,0.22)","#fbbf24"),
                ]
                c1, c2, c3 = st.columns(3, gap="small")
                for col, (icon, role, mail, pwd, bg, bor, clr) in zip([c1,c2,c3], accounts):
                    with col:
                        st.markdown(f"""<div style="background:{bg};border:1px solid {bor};
border-radius:12px;padding:.875rem .5rem;text-align:center;">
<div style="font-size:1.4rem;line-height:1;">{icon}</div>
<div style="font-weight:700;font-size:.78rem;color:{clr};margin:5px 0 4px;">{role}</div>
<div style="font-size:.62rem;color:{TEXT2};line-height:1.55;word-break:break-all;">{mail}<br>
<span style="font-family:monospace;opacity:.85;">{pwd}</span></div>
</div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)
            if not cognito.is_configured:
                st.info("Sign up not available in demo mode. Use a demo account above.")
            else:
                with st.form("signup_form", clear_on_submit=True):
                    st.text_input("Full Name", placeholder="John Doe")
                    st.text_input("Email", placeholder="you@company.com")
                    st.text_input("Password", type="password")
                    st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                        st.info("Registration coming soon")
