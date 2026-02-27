"""AgentFlow Finance Guard — SPA with custom nav column."""
import sys, logging, importlib
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import config
from i18n import t
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title=config.APP_NAME, page_icon="🛡️", layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": f"{config.APP_NAME} v{config.APP_VERSION}"},
)

for k, v in {"logged_in":False,"user_email":"","user_name":"","user_role":"viewer",
              "access_token":"","theme":"dark","language":"en","page":"Overview","show_logout_confirm":False}.items():
    if k not in st.session_state: st.session_state[k] = v

IS_DARK = st.session_state.theme == "dark"

try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    st.markdown(DARK_THEME if IS_DARK else LIGHT_THEME, unsafe_allow_html=True)
except Exception: pass

# Padding nuker
st.markdown("""<style>
section[data-testid="stMain"]>div,div[data-testid="stVerticalBlock"],
div[data-testid="stAppViewBlockContainer"] { padding-top:0!important; margin-top:0!important; }
.css-1y4p8pa,.css-z5fcl4,.css-ocqkz7,.css-1544g2n,.css-zt5igj,.e1tzin5v3,div.block-container {
    padding-top:0!important; padding-left:0!important; margin-top:0!important; }
[data-testid="stAppViewContainer"] { padding:0!important; }
[data-testid="ScrollToBottomContainer"]>div { padding:0!important; }
</style>""", unsafe_allow_html=True)

# ── LOGIN ─────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback; st.error(f"Login error: {e}"); st.code(traceback.format_exc())
    st.stop()

# ── LOGGED IN ────────────────────────────────────────────────────
IS_DARK  = st.session_state.theme == "dark"
ACC      = "#10b981"
ACC2     = "#059669"
BG_NAV   = "#141414" if IS_DARK else "#ffffff"
TEXT     = "#f5f5f5" if IS_DARK else "#0a0a0a"
TEXT2    = "#a3a3a3" if IS_DARK else "#737373"
TEXT3    = "#737373" if IS_DARK else "#a3a3a3"
BOR      = "#262626" if IS_DARK else "#e5e0da"
ACTIVE_BG= "rgba(16,185,129,.12)" if IS_DARK else "rgba(16,185,129,.08)"
HOVER_BG = "rgba(16,185,129,.07)" if IS_DARK else "rgba(16,185,129,.05)"
BTN_BG   = "#1f1f1f" if IS_DARK else "#f7f4f0"
ROLE_CLR = {"Admin":"#3b82f6","Analyst":"#10b981","Viewer":"#f59e0b"}

nm = st.session_state.user_name or "User"
rl = (st.session_state.user_role or "viewer").title()
em = st.session_state.user_email or ""
rc = ROLE_CLR.get(rl, "#a3a3a3")

PAGES = [
    ("Overview","📊"),("Upload","📄"),("Fraud","🚨"),
    ("ML Insights","🧠"),("Security","🛡️"),("Observability","📈"),
    ("Merchant","💼"),("Integrations","🔗"),("Settings","⚙️"),
]
PAGE_TO_MOD = {
    "Overview":"page_overview","Upload":"page_upload","Fraud":"page_fraud",
    "ML_Insights":"page_ml","Security":"page_security","Observability":"page_observability",
    "Merchant":"page_merchant","Integrations":"page_integrations","Settings":"page_settings",
}
PAGE_KEY = {p: p.replace(" ","_") for p,_ in PAGES}
PAGE_LABELS = {
    "Overview":"overview","Upload":"upload","Fraud":"fraud","ML Insights":"ml_insights",
    "Security":"security","Observability":"observability","Merchant":"merchant",
    "Integrations":"integrations","Settings":"settings",
}

# Override nav button styles
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

/* Nav column overrides */
[data-testid="column"]:first-of-type .stButton>button {{
  font-family:'DM Sans',sans-serif!important;
  font-weight:500!important;
  font-size:.82rem!important;
  text-align:left!important;
  justify-content:flex-start!important;
  border-radius:9px!important;
  border:1.5px solid transparent!important;
  background:transparent!important;
  color:{TEXT2}!important;
  padding:.5rem .75rem!important;
  transition:all .15s ease!important;
  box-shadow:none!important;
  margin-bottom:1px!important;
}}
[data-testid="column"]:first-of-type .stButton>button:hover {{
  background:{HOVER_BG}!important;
  border-color:{ACC}!important;
  color:{ACC}!important;
  transform:none!important;
}}
[data-testid="column"]:first-of-type .stButton>button[kind="primary"] {{
  background:{ACTIVE_BG}!important;
  border:1.5px solid rgba(16,185,129,.4)!important;
  color:{ACC}!important;
  font-weight:700!important;
  box-shadow:2px 2px 0px rgba(16,185,129,.15)!important;
}}
[data-testid="column"]:first-of-type .stButton>button[kind="primary"]:hover {{
  background:{ACTIVE_BG}!important;
  transform:none!important;
}}
/* Small utility buttons (theme/lang/logout) in nav */
[data-testid="column"]:first-of-type div[data-testid="stColumns"] .stButton>button {{
  font-size:.75rem!important;
  padding:.35rem .5rem!important;
}}
[data-testid="column"]:first-of-type hr {{
  border:none!important;
  border-top:1.5px solid {BOR}!important;
  margin:.75rem 0!important;
}}
</style>""", unsafe_allow_html=True)

nav_col, content_col = st.columns([1, 4], gap="small")

with nav_col:
    # Logo block
    st.markdown(f"""<div style="padding:1.5rem .875rem 1.25rem;text-align:center;
      border-bottom:2px solid {BOR};margin-bottom:.875rem;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
        width:52px;height:52px;border-radius:12px;
        background:linear-gradient(135deg,{ACC},{ACC2});
        border:2px solid {ACC2};box-shadow:3px 3px 0px {ACC2};
        font-size:1.6rem;margin-bottom:.6rem;">🛡️</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;
        color:{TEXT};letter-spacing:-.02em;">AgentFlow</div>
      <div style="font-family:'DM Sans',sans-serif;font-size:.58rem;color:{TEXT3};
        text-transform:uppercase;letter-spacing:.12em;margin-top:2px;">Finance Guard</div>
    </div>""", unsafe_allow_html=True)

    # User card
    st.markdown(f"""<div style="margin:0 .75rem .875rem;padding:.75rem;
      background:{ACTIVE_BG};border:1.5px solid rgba(16,185,129,.25);border-radius:10px;
      box-shadow:2px 2px 0px rgba(16,185,129,.1);">
      <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.82rem;
        color:{TEXT};">{nm}</div>
      <div style="font-family:'DM Sans',sans-serif;font-size:.68rem;color:{rc};
        font-weight:600;margin-top:2px;display:flex;align-items:center;gap:.35rem;">
        <span style="width:5px;height:5px;background:{rc};border-radius:50%;display:inline-block;"></span>{rl}
      </div>
      <div style="font-family:'DM Sans',sans-serif;font-size:.6rem;color:{TEXT3};
        margin-top:2px;word-break:break-all;">{em}</div>
    </div>""", unsafe_allow_html=True)

    # Nav label
    st.markdown(f"""<div style="padding:0 .875rem .35rem;font-family:'Syne',sans-serif;
      font-size:.58rem;font-weight:700;color:{TEXT3};text-transform:uppercase;
      letter-spacing:.12em;">{t('navigation')}</div>""", unsafe_allow_html=True)

    # Nav buttons
    for pname, icon in PAGES:
        pkey = PAGE_KEY[pname]
        is_active = st.session_state.page == pkey
        label_key = PAGE_LABELS.get(pname, pname.lower())
        display_name = t(label_key)
        if st.button(f"{icon}  {display_name}", key=f"nav_{pkey}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pkey; st.rerun()

    st.divider()

    # Theme + Lang toggles
    lang = st.session_state.get("language","en")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️", use_container_width=True, key="th_l",
                     type="primary" if not IS_DARK else "secondary", help="Light mode"):
            st.session_state.theme = "light"; st.rerun()
    with c2:
        if st.button("🌙", use_container_width=True, key="th_d",
                     type="primary" if IS_DARK else "secondary", help="Dark mode"):
            st.session_state.theme = "dark"; st.rerun()

    l1, l2 = st.columns(2)
    with l1:
        if st.button("🇬🇧", use_container_width=True, key="lang_en",
                     type="primary" if lang=="en" else "secondary", help="English"):
            st.session_state.language = "en"; st.rerun()
    with l2:
        if st.button("🇻🇳", use_container_width=True, key="lang_vi",
                     type="primary" if lang=="vi" else "secondary", help="Tiếng Việt"):
            st.session_state.language = "vi"; st.rerun()

    st.markdown('<div style="height:.25rem"></div>', unsafe_allow_html=True)

    # Logout
    if not st.session_state.show_logout_confirm:
        if st.button(f"🚪 {t('logout')}", use_container_width=True, key="lo_btn"):
            st.session_state.show_logout_confirm = True; st.rerun()
    else:
        st.warning(t("confirm_logout"))
        a, b = st.columns(2)
        with a:
            if st.button(t("yes"), type="primary", use_container_width=True, key="lo_y"):
                from auth.login import logout
                logout()
        with b:
            if st.button(t("no"), use_container_width=True, key="lo_n"):
                st.session_state.show_logout_confirm = False; st.rerun()

    st.markdown(f'<div style="text-align:center;color:{TEXT3};font-family:\'DM Sans\',sans-serif;'
                f'font-size:.58rem;padding:.75rem 0 .5rem;">v{config.APP_VERSION}</div>',
                unsafe_allow_html=True)

with content_col:
    st.markdown('<div style="padding:1.75rem 2rem 4rem 2.25rem;">', unsafe_allow_html=True)
    mod_name = PAGE_TO_MOD.get(st.session_state.page, "page_overview")
    try:
        mod = importlib.import_module(f"pages.{mod_name}")
        mod.render()
    except Exception as e:
        import traceback
        st.error(f"Page error on '{st.session_state.page}': {e}")
        st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)
