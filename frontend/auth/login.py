import streamlit as st
from auth.cognito_client import get_cognito_client
from config import config
from i18n import t


def logout():
    """Clear all session state and log out the current user."""
    for k in ["logged_in", "user_email", "user_name", "user_role", "access_token"]:
        st.session_state[k] = False if k == "logged_in" else ""
    st.session_state.page = "Overview"
    st.session_state.show_logout_confirm = False
    st.rerun()


def login_user(email: str, password: str, cognito) -> bool:
    result = cognito.login(email, password)
    if result['success']:
        st.session_state.logged_in    = True
        st.session_state.user_email   = email
        st.session_state.access_token = result.get('access_token', '')
        demo = config.DEMO_USERS.get(email, {})
        st.session_state.user_name = demo.get('name', email.split('@')[0].title())
        st.session_state.user_role = demo.get('role', 'viewer')
        return True
    return False


def login_page():
    IS_DARK = st.session_state.get('theme', 'dark') == 'dark'
    lang    = st.session_state.get('language', 'en')

    CARD = "#0b101e" if IS_DARK else "#ffffff"
    BOR  = "rgba(59,130,246,0.25)" if IS_DARK else "rgba(37,99,235,0.15)"
    TEXT = "#f1f5f9" if IS_DARK else "#0f172a"
    TEXT2 = "#64748b"
    INP  = "#111827" if IS_DARK else "#f8faff"
    BG   = "#060912" if IS_DARK else "#f0f4ff"
    GR1, GR2 = ("#3b82f6","#06b6d4") if IS_DARK else ("#2563eb","#0891b2")

    st.markdown(f"""<style>
    .main .block-container{{padding:0!important;max-width:100%!important;margin:0!important;}}
    .stApp{{background:{BG}!important;}}
    .stApp::before{{content:'';position:fixed;top:-200px;left:-200px;width:650px;height:650px;
      border-radius:50%;background:radial-gradient(circle,{"rgba(59,130,246,0.10)" if IS_DARK else "rgba(37,99,235,0.07)"} 0%,transparent 65%);
      animation:orbA 14s ease-in-out infinite;pointer-events:none;z-index:0;}}
    .stApp::after{{content:'';position:fixed;bottom:-180px;right:-180px;width:550px;height:550px;
      border-radius:50%;background:radial-gradient(circle,{"rgba(6,182,212,0.08)" if IS_DARK else "rgba(8,145,178,0.06)"} 0%,transparent 65%);
      animation:orbB 18s ease-in-out infinite;pointer-events:none;z-index:0;}}
    @keyframes orbA{{0%,100%{{transform:translate(0,0);}}33%{{transform:translate(70px,50px);}}66%{{transform:translate(-35px,80px);}}}}
    @keyframes orbB{{0%,100%{{transform:translate(0,0);}}40%{{transform:translate(-60px,-50px);}}70%{{transform:translate(40px,-30px);}}}}
    .stTextInput>div>div>input{{background:{INP}!important;border:1px solid {BOR}!important;
      border-radius:9px!important;color:{TEXT}!important;padding:.7rem 1rem!important;font-size:.9rem!important;}}
    .stTextInput>div>div>input:focus{{border-color:{GR1}!important;box-shadow:0 0 0 3px rgba(59,130,246,.12)!important;}}
    .stTextInput label{{color:{TEXT2}!important;font-size:.72rem!important;text-transform:uppercase!important;
      letter-spacing:.08em!important;font-weight:600!important;}}
    .stButton>button[kind="primary"]{{background:linear-gradient(135deg,{GR1},{GR2})!important;
      border:none!important;color:#fff!important;font-weight:600!important;padding:.75rem!important;
      font-size:.95rem!important;border-radius:9px!important;
      box-shadow:0 4px 20px rgba(59,130,246,.35)!important;transition:all .2s!important;}}
    .stButton>button[kind="primary"]:hover{{transform:translateY(-2px)!important;
      box-shadow:0 8px 28px rgba(59,130,246,.5)!important;color:#fff!important;}}
    .stButton>button:not([kind="primary"]){{background:{"rgba(255,255,255,0.07)" if IS_DARK else "rgba(0,0,0,0.04)"}!important;
      border:1px solid {BOR}!important;color:{TEXT2}!important;border-radius:8px!important;
      font-size:.8rem!important;padding:.35rem .75rem!important;}}
    [data-testid="stTabs"]{{border-bottom:1px solid {BOR}!important;margin-bottom:.25rem!important;}}
    [data-testid="stTabs"] button{{color:{TEXT2}!important;font-weight:600!important;font-size:.875rem!important;}}
    [data-testid="stTabs"] button[aria-selected="true"]{{color:{GR1}!important;border-bottom:2px solid {GR1}!important;}}
    </style>""", unsafe_allow_html=True)

    # ── Top-right controls: language + theme ─────────────────────
    st.markdown('<div style="height:.75rem"></div>', unsafe_allow_html=True)
    _, ctrl = st.columns([5, 1])
    with ctrl:
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("🌙" if IS_DARK else "☀️", key="login_theme", use_container_width=True):
                st.session_state.theme = "light" if IS_DARK else "dark"
                st.rerun()
        with tc2:
            if st.button("🇻🇳" if lang == "en" else "🇬🇧", key="login_lang", use_container_width=True):
                st.session_state.language = "vi" if lang == "en" else "en"
                st.rerun()

    # ── Centered card ─────────────────────────────────────────────
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown(f"""
<div style="background:{CARD};border:1px solid {BOR};border-radius:20px;
  padding:2.25rem 2rem 1.75rem;margin-top:.5rem;
  box-shadow:0 32px 80px rgba(0,0,0,{'0.5' if IS_DARK else '0.1'}),0 0 0 1px rgba(59,130,246,.05);">
  <div style="text-align:center;margin-bottom:1.5rem;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
      width:64px;height:64px;border-radius:14px;
      background:linear-gradient(135deg,rgba(59,130,246,0.15),rgba(6,182,212,0.1));
      border:1px solid rgba(59,130,246,0.25);margin-bottom:.75rem;
      box-shadow:0 0 32px rgba(59,130,246,0.18);font-size:1.9rem;">🛡️</div>
    <div style="font-size:1.45rem;font-weight:700;letter-spacing:-.02em;
      background:linear-gradient(135deg,{GR1},{GR2});
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
      {config.APP_NAME}</div>
    <div style="font-size:.75rem;color:{TEXT2};margin-top:3px;letter-spacing:.03em;">
      {t('app_subtitle')}</div>
  </div>
</div>""", unsafe_allow_html=True)

        cognito = get_cognito_client()
        tab1, tab2 = st.tabs([f"🔐  {t('sign_in')}", f"📝  {t('sign_up')}"])

        with tab1:
            st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input(t('email'), placeholder=t('email_placeholder'))
                password = st.text_input(t('password'), type="password", placeholder=t('pwd_placeholder'))
                st.markdown('<div style="height:.15rem"></div>', unsafe_allow_html=True)
                if st.form_submit_button(t('signin_btn'), use_container_width=True, type="primary"):
                    if not email:    st.error(t('enter_email'))
                    elif not password: st.error(t('enter_password'))
                    else:
                        with st.spinner(t('signing_in')):
                            if login_user(email, password, cognito): st.rerun()
                            else: st.error(t('invalid_creds'))

            if not cognito.is_configured:
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:.5rem;margin:1.2rem 0 .75rem;">
  <div style="flex:1;height:1px;background:{'rgba(255,255,255,0.07)' if IS_DARK else 'rgba(0,0,0,0.07)'}"></div>
  <span style="font-size:.62rem;color:{TEXT2};font-weight:700;text-transform:uppercase;letter-spacing:.1em;">{t('demo_accounts')}</span>
  <div style="flex:1;height:1px;background:{'rgba(255,255,255,0.07)' if IS_DARK else 'rgba(0,0,0,0.07)'}"></div>
</div>""", unsafe_allow_html=True)

                accounts = [
                    ("👑","Admin","admin@agentflow.ai","Admin@2026!","rgba(59,130,246,0.1)","rgba(59,130,246,0.22)","#60a5fa"),
                    ("🔍","Analyst","analyst@agentflow.ai","Analyst@2026!","rgba(16,185,129,0.1)","rgba(16,185,129,0.22)","#34d399"),
                    ("👤","Viewer","viewer@agentflow.ai","Viewer@2026!","rgba(245,158,11,0.1)","rgba(245,158,11,0.22)","#fbbf24"),
                ]
                c1,c2,c3 = st.columns(3)
                for col,(icon,role,mail,pwd,bg,bor,clr) in zip([c1,c2,c3], accounts):
                    with col:
                        st.markdown(f"""<div style="background:{bg};border:1px solid {bor};
border-radius:11px;padding:.8rem .5rem;text-align:center;margin-bottom:.25rem;">
<div style="font-size:1.3rem;line-height:1;">{icon}</div>
<div style="font-weight:700;font-size:.75rem;color:{clr};margin:4px 0 3px;">{role}</div>
<div style="font-size:.6rem;color:{TEXT2};line-height:1.55;word-break:break-all;">{mail}<br>
<span style="font-family:monospace;opacity:.8;font-size:.58rem;">{pwd}</span></div>
</div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
            if not cognito.is_configured:
                st.info(t('signup_unavailable'))
            else:
                with st.form("signup_form", clear_on_submit=True):
                    st.text_input(t('full_name'), placeholder=t('name_placeholder'))
                    st.text_input(t('email'), placeholder="you@company.com")
                    st.text_input(t('password'), type="password")
                    st.text_input(t('confirm_password'), type="password")
                    if st.form_submit_button(t('create_account'), use_container_width=True, type="primary"):
                        st.info(t('reg_coming_soon'))

        st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
