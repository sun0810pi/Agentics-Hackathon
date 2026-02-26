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
    BG      = "#050810" if IS_DARK else "#f0f4ff"
    CARD    = "#0b101e" if IS_DARK else "#ffffff"
    BOR     = "rgba(59,130,246,0.25)" if IS_DARK else "rgba(37,99,235,0.15)"
    TEXT    = "#f1f5f9" if IS_DARK else "#0f172a"
    TEXT2   = "#64748b"
    INP     = "#111827" if IS_DARK else "#f8faff"

    st.markdown(f"""<style>
    /* ── Full page reset ── */
    .main .block-container{{padding:0!important;max-width:100%!important;margin:0!important;}}
    
    /* ── Animated background ── */
    .stApp>[data-testid="stAppViewContainer"]{{
        background:{BG}!important;
        overflow:hidden;
    }}
    
    /* Orb 1 - blue */
    .stApp>[data-testid="stAppViewContainer"]::before{{
        content:'';
        position:fixed;
        width:600px; height:600px;
        border-radius:50%;
        background:radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%);
        top:-100px; left:-150px;
        animation:orbFloat1 8s ease-in-out infinite;
        pointer-events:none;
        z-index:0;
    }}
    /* Orb 2 - cyan */
    .stApp>[data-testid="stAppViewContainer"]::after{{
        content:'';
        position:fixed;
        width:500px; height:500px;
        border-radius:50%;
        background:radial-gradient(circle, rgba(6,182,212,0.14) 0%, transparent 70%);
        bottom:-80px; right:-100px;
        animation:orbFloat2 10s ease-in-out infinite;
        pointer-events:none;
        z-index:0;
    }}
    
    @keyframes orbFloat1{{
        0%,100%{{transform:translate(0,0) scale(1);}}
        33%{{transform:translate(60px,40px) scale(1.08);}}
        66%{{transform:translate(-30px,70px) scale(0.95);}}
    }}
    @keyframes orbFloat2{{
        0%,100%{{transform:translate(0,0) scale(1);}}
        40%{{transform:translate(-70px,-50px) scale(1.1);}}
        70%{{transform:translate(40px,-30px) scale(0.92);}}
    }}
    
    /* Grid lines overlay */
    .login-grid{{
        position:fixed;
        inset:0;
        background-image:
            linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
        background-size:40px 40px;
        pointer-events:none;
        z-index:0;
    }}
    
    /* Card above background */
    .login-card-wrap{{position:relative;z-index:1;}}
    
    /* ── Inputs ── */
    .stTextInput>div>div>input{{
        background:{INP}!important;border:1px solid {BOR}!important;
        border-radius:10px!important;color:{TEXT}!important;
        padding:0.75rem 1rem!important;font-size:0.9rem!important;
        transition:border-color .2s, box-shadow .2s!important;
    }}
    .stTextInput>div>div>input:focus{{
        border-color:#3b82f6!important;
        box-shadow:0 0 0 3px rgba(59,130,246,0.15)!important;
    }}
    .stTextInput label{{
        color:{TEXT2}!important;font-size:0.78rem!important;
        text-transform:uppercase!important;letter-spacing:.06em!important;font-weight:500!important;
    }}
    
    /* ── Sign in button ── */
    .stButton>button[kind="primary"]{{
        background:linear-gradient(135deg,#3b82f6,#06b6d4)!important;
        border:none!important;color:#fff!important;font-weight:600!important;
        padding:0.75rem!important;font-size:0.95rem!important;
        border-radius:10px!important;letter-spacing:.01em!important;
        box-shadow:0 4px 24px rgba(59,130,246,0.4)!important;
        transition:all .2s!important;
    }}
    .stButton>button[kind="primary"]:hover{{
        transform:translateY(-2px)!important;
        box-shadow:0 8px 32px rgba(59,130,246,0.55)!important;color:#fff!important;
    }}
    
    /* ── Tabs ── */
    [data-testid="stTabs"]{{border-bottom:1px solid {BOR}!important;}}
    [data-testid="stTabs"] button{{
        color:{TEXT2}!important;font-weight:600!important;font-size:0.875rem!important;
        padding:.6rem 1.25rem!important;
    }}
    [data-testid="stTabs"] button[aria-selected="true"]{{
        color:#3b82f6!important;border-bottom:2px solid #3b82f6!important;
    }}
    </style>
    
    <div class="login-grid"></div>
    """, unsafe_allow_html=True)

    # Layout: centered card
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown(f"""
<div class="login-card-wrap">
<div style="background:{CARD};border:1px solid {BOR};border-radius:22px;
    padding:2.75rem 2.25rem 2rem;margin-top:2.5rem;
    box-shadow:0 40px 100px rgba(0,0,0,{'0.6' if IS_DARK else '0.12'}),
               0 0 0 1px rgba(59,130,246,0.08);">

  <div style="text-align:center;margin-bottom:2rem;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
      width:72px;height:72px;border-radius:18px;
      background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(6,182,212,0.1));
      border:1px solid rgba(59,130,246,0.25);margin-bottom:1rem;
      box-shadow:0 0 40px rgba(59,130,246,0.2);
      font-size:2.2rem;">🛡️</div>
    <div style="font-size:1.6rem;font-weight:700;letter-spacing:-.025em;
      background:linear-gradient(135deg,#3b82f6,#06b6d4);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      {config.APP_NAME}</div>
    <div style="font-size:0.78rem;color:{TEXT2};margin-top:5px;letter-spacing:.04em;">
      {config.HACKATHON}</div>
  </div>

</div></div>""", unsafe_allow_html=True)

        cognito = get_cognito_client()
        tab1, tab2 = st.tabs(["🔐  Sign In", "📝  Sign Up"])

        with tab1:
            st.markdown('<div style="height:.5rem;"></div>', unsafe_allow_html=True)
            with st.form("lf", clear_on_submit=False):
                email    = st.text_input("Email address", placeholder="admin@agentflow.ai", key="l_em")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="l_pw")
                st.markdown('<div style="height:.25rem;"></div>', unsafe_allow_html=True)
                if st.form_submit_button("Sign In  →", use_container_width=True, type="primary"):
                    if not email: st.error("Enter your email")
                    elif not password: st.error("Enter your password")
                    else:
                        with st.spinner("Signing in..."):
                            if login_user(email, password, cognito): st.rerun()
                            else: st.error("❌ Invalid credentials")

            # Demo accounts
            if config.get_demo_mode() == "demo" or not cognito.is_configured:
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.75rem;margin:1.5rem 0 1rem;">
  <div style="flex:1;height:1px;background:{'rgba(255,255,255,0.08)' if IS_DARK else 'rgba(0,0,0,0.07)'}"></div>
  <div style="font-size:0.68rem;color:{TEXT2};font-weight:600;text-transform:uppercase;letter-spacing:.1em;white-space:nowrap;">
    Demo Accounts</div>
  <div style="flex:1;height:1px;background:{'rgba(255,255,255,0.08)' if IS_DARK else 'rgba(0,0,0,0.07)'}"></div>
</div>""", unsafe_allow_html=True)

                accounts = [
                    ("👑","Admin","admin@agentflow.ai","Admin@2026!",
                     "rgba(59,130,246,0.1)","rgba(59,130,246,0.2)","#60a5fa"),
                    ("🔍","Analyst","analyst@agentflow.ai","Analyst@2026!",
                     "rgba(16,185,129,0.1)","rgba(16,185,129,0.2)","#34d399"),
                    ("👤","Viewer","viewer@agentflow.ai","Viewer@2026!",
                     "rgba(245,158,11,0.1)","rgba(245,158,11,0.2)","#fbbf24"),
                ]
                c1,c2,c3 = st.columns(3)
                for col,(icon,role,mail,pwd,bg,bor,clr) in zip([c1,c2,c3], accounts):
                    with col:
                        st.markdown(f"""
<div style="background:{bg};border:1px solid {bor};border-radius:12px;
    padding:1rem 0.6rem;text-align:center;cursor:default;">
  <div style="font-size:1.5rem;line-height:1;">{icon}</div>
  <div style="font-weight:700;font-size:0.8rem;color:{clr};margin:6px 0 4px;">{role}</div>
  <div style="font-size:0.65rem;color:{TEXT2};line-height:1.5;">{mail}<br>
    <span style="font-family:monospace;font-size:0.62rem;">{pwd}</span></div>
</div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="height:.5rem;"></div>', unsafe_allow_html=True)
            if not cognito.is_configured:
                st.info("Sign up is not available in demo mode. Use a demo account.")
            else:
                with st.form("sf", clear_on_submit=True):
                    st.text_input("Full Name", placeholder="John Doe")
                    st.text_input("Email", placeholder="you@company.com")
                    st.text_input("Password", type="password")
                    st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                        st.info("Registration coming soon")
