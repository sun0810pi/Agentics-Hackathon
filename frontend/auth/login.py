import streamlit as st
from auth.cognito_client import get_cognito_client
from config import config
from i18n import t


def logout():
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

    # Portfolio palette
    BLACK  = "#0a0a0a"
    WHITE  = "#ffffff"
    ACC    = "#10b981"
    G100   = "#f5f5f5"
    G200   = "#e5e5e5"
    G300   = "#d4d4d4"
    G400   = "#a3a3a3"
    G500   = "#737373"
    G700   = "#404040"
    G800   = "#262626"
    G900   = "#171717"

    BG      = G900 if IS_DARK else G100
    CARD_BG = G800 if IS_DARK else WHITE
    CARD_BOR = G700 if IS_DARK else BLACK
    TEXT    = WHITE if IS_DARK else BLACK
    TEXT2   = G400 if IS_DARK else G500
    INP_BG  = G900 if IS_DARK else WHITE
    INP_BOR = G700 if IS_DARK else G300
    DIV_CLR = G800 if IS_DARK else G200
    DEMO_BG = G900 if IS_DARK else G100

    SHADOW    = f"4px 4px 0px {BLACK}"
    SHADOW_ACC = f"4px 4px 0px rgba(16,185,129,0.5)"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

.main .block-container{{padding:0!important;max-width:100%!important;margin:0!important;}}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{{display:none!important;}}
.stApp{{background:{BG}!important;font-family:'DM Sans',sans-serif!important;}}

/* Dot grid background */
.stApp::before{{
  content:'';position:fixed;inset:0;z-index:0;
  background-image: radial-gradient({'rgba(255,255,255,0.07)' if IS_DARK else 'rgba(0,0,0,0.08)'} 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events:none;
}}

/* Inputs */
.stTextInput>div>div>input{{
  font-family:'DM Sans',sans-serif!important;
  background:{INP_BG}!important;border:2px solid {INP_BOR}!important;
  border-radius:0!important;padding:.75rem 1rem!important;font-size:.9rem!important;
  color:{TEXT}!important;transition:border-color .2s!important;box-shadow:none!important;
}}
.stTextInput>div>div>input:focus{{
  border-color:{ACC}!important;box-shadow:none!important;
  outline:2px solid rgba(16,185,129,.25)!important;outline-offset:0!important;
}}
.stTextInput label{{
  font-family:'JetBrains Mono',monospace!important;font-weight:500!important;
  font-size:.72rem!important;color:{TEXT2}!important;text-transform:uppercase!important;letter-spacing:.08em!important;
}}

/* Primary button - neo-brutalist */
.stButton>button[kind="primary"]{{
  font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:.95rem!important;
  background:{ACC}!important;color:{BLACK}!important;
  border:2px solid {BLACK}!important;border-radius:0!important;padding:.8rem 1.5rem!important;
  width:100%!important;box-shadow:{SHADOW}!important;transition:all .15s ease!important;
}}
.stButton>button[kind="primary"]:hover{{
  transform:translate(4px,4px)!important;box-shadow:none!important;
}}
.stButton>button[kind="primary"]:active{{transform:translate(4px,4px)!important;box-shadow:none!important;}}

/* Secondary buttons */
.stButton>button:not([kind="primary"]){{
  font-family:'DM Sans',sans-serif!important;
  background:{'rgba(255,255,255,0.06)' if IS_DARK else WHITE}!important;
  border:2px solid {INP_BOR}!important;color:{TEXT2}!important;
  border-radius:0!important;font-size:.78rem!important;padding:.35rem .75rem!important;
  box-shadow:{'2px 2px 0px rgba(255,255,255,0.05)' if IS_DARK else '2px 2px 0px rgba(0,0,0,0.12)'}!important;
  transition:all .15s!important;
}}
.stButton>button:not([kind="primary"]):hover{{
  transform:translate(2px,2px)!important;box-shadow:none!important;
  border-color:{ACC}!important;color:{ACC}!important;
}}

/* Tabs */
[data-testid="stTabs"] button{{
  font-family:'DM Sans',sans-serif!important;font-weight:600!important;
  font-size:.875rem!important;color:{TEXT2}!important;border-radius:0!important;
}}
[data-testid="stTabs"] button[aria-selected="true"]{{
  font-family:'Syne',sans-serif!important;font-weight:700!important;
  color:{ACC if IS_DARK else BLACK}!important;
  border-bottom:3px solid {ACC if IS_DARK else BLACK}!important;
  background:{'rgba(16,185,129,.06)' if IS_DARK else G100}!important;
}}
[data-testid="stTabs"] {{border-bottom:2px solid {DIV_CLR}!important;}}

[data-testid="stAlert"]{{border-radius:0!important;border:2px solid {ACC}!important;}}
</style>""", unsafe_allow_html=True)

    # ── Top controls ──────────────────────────────────────────────
    st.markdown('<div style="height:.75rem"></div>', unsafe_allow_html=True)
    _, ctrl = st.columns([5, 1])
    with ctrl:
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("🌙" if IS_DARK else "☀️", key="login_theme", use_container_width=True):
                st.session_state.theme = "light" if IS_DARK else "dark"; st.rerun()
        with tc2:
            if st.button("🇻🇳" if lang == "en" else "🇬🇧", key="login_lang", use_container_width=True):
                st.session_state.language = "vi" if lang == "en" else "en"; st.rerun()

    # ── Centered card ─────────────────────────────────────────────
    _, mid, _ = st.columns([1, 1.05, 1])
    with mid:
        # Header card — portfolio style: black bg, hard shadow
        st.markdown(f"""
<div style="position:relative;z-index:1;margin-top:.5rem;">
  <!-- Logo bar -->
  <div style="background:{BLACK};border:2px solid {BLACK};box-shadow:{SHADOW};
    padding:1.75rem 2rem 1.5rem;margin-bottom:0;">
    <div style="display:flex;align-items:center;gap:1rem;">
      <div style="width:52px;height:52px;background:{ACC};color:{BLACK};
        display:flex;align-items:center;justify-content:center;
        border:2px solid {BLACK};box-shadow:2px 2px 0 rgba(0,0,0,0.3);
        font-size:1.6rem;flex-shrink:0;">🛡️</div>
      <div>
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.4rem;
          color:{WHITE};letter-spacing:-.03em;line-height:1;">{config.APP_NAME}</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;
          color:rgba(255,255,255,0.5);margin-top:.2rem;letter-spacing:.04em;">{t('app_subtitle')}</div>
      </div>
      <div style="margin-left:auto;display:flex;align-items:center;gap:.4rem;
        background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.4);
        padding:.3rem .75rem;font-family:'JetBrains Mono',monospace;
        font-size:.65rem;color:{ACC};letter-spacing:.06em;">
        <span style="width:6px;height:6px;background:{ACC};border-radius:50%;display:inline-block;
          animation:pulse 2s infinite;"></span> ONLINE
      </div>
    </div>
  </div>

  <!-- Form area -->
  <div style="background:{CARD_BG};border:2px solid {CARD_BOR};border-top:none;
    padding:0 2rem 1.5rem;">
</div>
<style>@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.3;}}}}</style>
""", unsafe_allow_html=True)

        cognito = get_cognito_client()
        tab1, tab2 = st.tabs([f"🔐  {t('sign_in')}", f"📝  {t('sign_up')}"])

        with tab1:
            st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input(t('email'), placeholder=t('email_placeholder'))
                password = st.text_input(t('password'), type="password", placeholder=t('pwd_placeholder'))
                st.markdown('<div style="height:.35rem"></div>', unsafe_allow_html=True)
                if st.form_submit_button(t('signin_btn'), use_container_width=True, type="primary"):
                    if not email:      st.error(t('enter_email'))
                    elif not password: st.error(t('enter_password'))
                    else:
                        with st.spinner(t('signing_in')):
                            if login_user(email, password, cognito): st.rerun()
                            else: st.error(t('invalid_creds'))

            if not cognito.is_configured:
                # Divider
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:.75rem;margin:1.5rem 0 1rem;">
  <div style="flex:1;height:2px;background:{DIV_CLR};"></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:.62rem;color:{TEXT2};
    font-weight:500;text-transform:uppercase;letter-spacing:.1em;white-space:nowrap;">
    {t('demo_accounts')}
  </span>
  <div style="flex:1;height:2px;background:{DIV_CLR};"></div>
</div>""", unsafe_allow_html=True)

                # Demo account cards — project-card style from portfolio
                accounts = [
                    ("👑","Admin",   "admin@agentflow.ai",   "Admin@2026!",   "#3b82f6","rgba(59,130,246,.15)","rgba(59,130,246,.4)"),
                    ("🔍","Analyst", "analyst@agentflow.ai", "Analyst@2026!", ACC,      "rgba(16,185,129,.15)","rgba(16,185,129,.4)"),
                    ("👤","Viewer",  "viewer@agentflow.ai",  "Viewer@2026!",  "#f59e0b","rgba(245,158,11,.15)","rgba(245,158,11,.4)"),
                ]
                c1, c2, c3 = st.columns(3)
                for col, (icon, role, mail, pwd, clr, bg, bor) in zip([c1,c2,c3], accounts):
                    with col:
                        st.markdown(f"""<div style="background:{DEMO_BG};border:2px solid {G800 if IS_DARK else G200};
padding:.85rem .6rem;text-align:center;transition:border-color .2s;box-shadow:2px 2px 0 {'rgba(255,255,255,0.04)' if IS_DARK else 'rgba(0,0,0,0.08)'};">
<div style="font-size:1.3rem;line-height:1;margin-bottom:.4rem;">{icon}</div>
<div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.72rem;
  color:{clr};margin-bottom:.3rem;text-transform:uppercase;letter-spacing:.05em;">{role}</div>
<div style="font-family:'JetBrains Mono',monospace;font-size:.56rem;
  color:{TEXT2};word-break:break-all;line-height:1.7;">{mail}<br>
  <span style="color:{TEXT2};opacity:.7;">{pwd}</span></div>
</div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
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

        # Footer
        st.markdown(f"""<div style="text-align:center;margin-top:1.25rem;padding-top:.875rem;
border-top:2px solid {DIV_CLR};">
<span style="font-family:'JetBrains Mono',monospace;font-size:.6rem;color:{TEXT2};">
v{config.APP_VERSION} &nbsp;·&nbsp; AgentFlow Finance Guard &nbsp;·&nbsp; Enterprise</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
