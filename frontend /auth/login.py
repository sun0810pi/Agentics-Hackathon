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

    BG       = "#0a0a0a" if IS_DARK else "#f0ede8"
    CARD_BG  = "#141414" if IS_DARK else "#ffffff"
    ACC      = "#10b981"
    ACC2     = "#059669"
    TEXT     = "#f5f5f5" if IS_DARK else "#0a0a0a"
    TEXT2    = "#a3a3a3" if IS_DARK else "#737373"
    INP_BG   = "#1f1f1f" if IS_DARK else "#fafafa"
    INP_BOR  = "#333333" if IS_DARK else "#d4d4d4"
    DIV_CLR  = "#242424" if IS_DARK else "#e5e5e5"
    DEMO_BG  = "#1a1a1a" if IS_DARK else "#fafafa"
    DEMO_BOR = "#2a2a2a" if IS_DARK else "#e5e5e5"
    GRID_CLR = "rgba(255,255,255,0.03)" if IS_DARK else "rgba(0,0,0,0.04)"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
.main .block-container{{padding:0!important;max-width:100%!important;margin:0!important;}}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{{display:none!important;}}
.stApp{{background:{BG}!important;font-family:'DM Sans',sans-serif!important;}}
.stApp::before{{content:'';position:fixed;inset:0;
  background-image:linear-gradient({GRID_CLR} 1px,transparent 1px),linear-gradient(90deg,{GRID_CLR} 1px,transparent 1px);
  background-size:40px 40px;pointer-events:none;z-index:0;}}
.stTextInput>div>div>input{{font-family:'DM Sans',sans-serif!important;background:{INP_BG}!important;
  border:2px solid {INP_BOR}!important;border-radius:10px!important;padding:.75rem 1rem!important;
  font-size:.95rem!important;color:{TEXT}!important;transition:all .2s ease!important;box-shadow:none!important;}}
.stTextInput>div>div>input:focus{{border-color:{ACC}!important;box-shadow:0 0 0 3px rgba(16,185,129,.15)!important;}}
.stTextInput label{{font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:.78rem!important;
  color:{TEXT}!important;text-transform:uppercase!important;letter-spacing:.07em!important;}}
.stButton>button[kind="primary"]{{font-family:'Syne',sans-serif!important;font-weight:700!important;
  font-size:.95rem!important;background:{ACC}!important;color:#ffffff!important;
  border:2.5px solid {ACC2}!important;border-radius:10px!important;padding:.8rem 1.5rem!important;
  width:100%!important;box-shadow:4px 4px 0px {ACC2}!important;transition:all .15s ease!important;}}
.stButton>button[kind="primary"]:hover{{transform:translate(-2px,-2px)!important;box-shadow:6px 6px 0px {ACC2}!important;}}
.stButton>button[kind="primary"]:active{{transform:translate(2px,2px)!important;box-shadow:2px 2px 0px {ACC2}!important;}}
.stButton>button:not([kind="primary"]){{font-family:'DM Sans',sans-serif!important;
  background:{'rgba(255,255,255,0.07)' if IS_DARK else 'rgba(0,0,0,0.05)'}!important;
  border:1.5px solid {INP_BOR}!important;color:{TEXT2}!important;border-radius:8px!important;
  font-size:.8rem!important;padding:.4rem .75rem!important;transition:all .15s!important;}}
.stButton>button:not([kind="primary"]):hover{{border-color:{ACC}!important;color:{ACC}!important;}}
[data-testid="stTabs"] button{{font-family:'Syne',sans-serif!important;font-weight:600!important;
  font-size:.875rem!important;color:{TEXT2}!important;}}
[data-testid="stTabs"] button[aria-selected="true"]{{color:{ACC}!important;border-bottom:2.5px solid {ACC}!important;}}
[data-testid="stAlert"]{{border-radius:10px!important;}}
</style>""", unsafe_allow_html=True)

    # Top controls
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

    _, mid, _ = st.columns([1, 1.05, 1])
    with mid:
        st.markdown(f"""
<div style="background:{CARD_BG};border:2.5px solid {ACC};border-radius:20px;
  padding:2.5rem 2.25rem 1.5rem;margin-top:.5rem;
  box-shadow:6px 6px 0px {ACC2},{'0 32px 80px rgba(0,0,0,0.5)' if IS_DARK else '0 8px 40px rgba(0,0,0,0.08)'};
  position:relative;z-index:1;">
  <div style="text-align:center;margin-bottom:1.75rem;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
      width:72px;height:72px;border-radius:16px;
      background:linear-gradient(135deg,{ACC},{ACC2});border:2.5px solid {ACC2};
      box-shadow:4px 4px 0px {ACC2};font-size:2rem;margin-bottom:1rem;">🛡️</div>
    <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.85rem;
      color:{TEXT};letter-spacing:-.03em;line-height:1;">{config.APP_NAME}</div>
    <div style="font-family:'DM Sans',sans-serif;font-size:.82rem;color:{TEXT2};
      margin-top:.35rem;letter-spacing:.02em;">{t('app_subtitle')}</div>
    <div style="margin-top:.85rem;display:flex;justify-content:center;">
      <div style="display:inline-flex;align-items:center;gap:.4rem;
        background:rgba(16,185,129,.1);border:1.5px solid rgba(16,185,129,.3);
        border-radius:8px;padding:.3rem .85rem;font-family:'DM Sans',sans-serif;
        font-size:.68rem;font-weight:600;color:{ACC};text-transform:uppercase;letter-spacing:.07em;">
        <span style="width:6px;height:6px;background:{ACC};border-radius:50%;display:inline-block;
          animation:pulse 2s infinite;"></span> System Online
      </div>
    </div>
  </div>
</div>
<style>@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.4;}}}}</style>
""", unsafe_allow_html=True)

        cognito = get_cognito_client()
        tab1, tab2 = st.tabs([f"🔐  {t('sign_in')}", f"📝  {t('sign_up')}"])

        with tab1:
            st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
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
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:.75rem;margin:1.5rem 0 1rem;">
  <div style="flex:1;height:2px;background:{DIV_CLR};border-radius:1px;"></div>
  <span style="font-family:'Syne',sans-serif;font-size:.62rem;color:{TEXT2};
    font-weight:700;text-transform:uppercase;letter-spacing:.12em;white-space:nowrap;">
    {t('demo_accounts')}
  </span>
  <div style="flex:1;height:2px;background:{DIV_CLR};border-radius:1px;"></div>
</div>""", unsafe_allow_html=True)

                accounts = [
                    ("👑","Admin","admin@agentflow.ai","Admin@2026!","#3b82f6","rgba(59,130,246,.15)","rgba(59,130,246,.28)"),
                    ("🔍","Analyst","analyst@agentflow.ai","Analyst@2026!","#10b981","rgba(16,185,129,.15)","rgba(16,185,129,.28)"),
                    ("👤","Viewer","viewer@agentflow.ai","Viewer@2026!","#f59e0b","rgba(245,158,11,.15)","rgba(245,158,11,.28)"),
                ]
                c1, c2, c3 = st.columns(3)
                for col, (icon, role, mail, pwd, clr, bg, bor) in zip([c1,c2,c3], accounts):
                    with col:
                        st.markdown(f"""<div style="background:{DEMO_BG};border:2px solid {bor};
border-radius:12px;padding:.9rem .6rem;text-align:center;box-shadow:3px 3px 0px {bor};">
<div style="font-size:1.4rem;line-height:1;margin-bottom:.4rem;">{icon}</div>
<div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.75rem;color:{clr};
  margin-bottom:.35rem;text-transform:uppercase;letter-spacing:.04em;">{role}</div>
<div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:{TEXT2};
  word-break:break-all;line-height:1.6;">{mail}<br><span style="opacity:.7;">{pwd}</span></div>
</div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
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

        st.markdown(f"""<div style="text-align:center;margin-top:1.5rem;padding-top:1rem;
border-top:2px solid {DIV_CLR};">
<span style="font-family:'DM Sans',sans-serif;font-size:.62rem;color:{TEXT2};">
AgentFlow Finance Guard · v{config.APP_VERSION} · Enterprise Security</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
