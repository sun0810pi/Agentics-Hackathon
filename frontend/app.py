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

st.markdown("""<style>
section[data-testid="stMain"] > div,
div[data-testid="stVerticalBlock"],
div[data-testid="stAppViewBlockContainer"] { padding-top:0!important; margin-top:0!important; }
.css-1y4p8pa,.css-z5fcl4,.css-ocqkz7,.css-1544g2n,.css-zt5igj,.e1tzin5v3,div.block-container {
    padding-top:0!important; padding-left:0!important; margin-top:0!important; }
[data-testid="stAppViewContainer"] { padding:0!important; }
[data-testid="ScrollToBottomContainer"] > div { padding:0!important; }
</style>""", unsafe_allow_html=True)

# ── LOGIN ─────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback; st.error(f"Login error: {e}"); st.code(traceback.format_exc())
    st.stop()

# ── LOGGED IN ─────────────────────────────────────────────────────
IS_DARK  = st.session_state.theme == "dark"

# Portfolio palette
BLACK   = "#0a0a0a"
WHITE   = "#ffffff"
ACC     = "#10b981"
G100    = "#f5f5f5"
G200    = "#e5e5e5"
G300    = "#d4d4d4"
G400    = "#a3a3a3"
G500    = "#737373"
G700    = "#404040"
G800    = "#262626"
G900    = "#171717"

NAV_BG  = "#141414" if IS_DARK else WHITE
NAV_BOR = G800 if IS_DARK else BLACK
TEXT    = WHITE if IS_DARK else BLACK
TEXT2   = G400 if IS_DARK else G500
TEXT3   = G500 if IS_DARK else G400
ROLE_CLR = {"Admin":"#3b82f6","Analyst":ACC,"Viewer":"#f59e0b"}

nm = st.session_state.user_name or "User"
rl = (st.session_state.user_role or "viewer").title()
em = st.session_state.user_email or ""
rc = ROLE_CLR.get(rl, G400)

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
PAGE_KEY    = {p: p.replace(" ","_") for p,_ in PAGES}
PAGE_LABELS = {
    "Overview":"overview","Upload":"upload","Fraud":"fraud","ML Insights":"ml_insights",
    "Security":"security","Observability":"observability","Merchant":"merchant",
    "Integrations":"integrations","Settings":"settings",
}

SHADOW_SM = f"2px 2px 0px {BLACK}"
ACT_BG = "rgba(16,185,129,.1)" if IS_DARK else "rgba(16,185,129,.07)"

# Nav button override CSS — portfolio style
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* All nav column buttons */
[data-testid="column"]:first-of-type .stButton>button {{
  font-family:'DM Sans',sans-serif!important;font-weight:500!important;
  font-size:.82rem!important;text-align:left!important;justify-content:flex-start!important;
  border-radius:0!important;border:2px solid transparent!important;
  background:transparent!important;color:{TEXT2}!important;
  padding:.5rem .875rem!important;transition:all .15s ease!important;
  box-shadow:none!important;margin-bottom:2px!important;
}}
[data-testid="column"]:first-of-type .stButton>button:hover {{
  background:{ACT_BG}!important;border-color:{ACC}!important;
  color:{ACC}!important;transform:none!important;
}}

/* Active nav button */
[data-testid="column"]:first-of-type .stButton>button[kind="primary"] {{
  font-family:'Syne',sans-serif!important;font-weight:700!important;
  background:{ACT_BG}!important;
  border:2px solid {ACC}!important;
  color:{ACC}!important;
  box-shadow:2px 2px 0px rgba(16,185,129,0.25)!important;
}}
[data-testid="column"]:first-of-type .stButton>button[kind="primary"]:hover {{
  background:{ACT_BG}!important;transform:none!important;color:{ACC}!important;
}}

/* Small utility row buttons (theme/lang) */
[data-testid="column"]:first-of-type [data-testid="stColumns"] .stButton>button {{
  font-size:.72rem!important;padding:.35rem .4rem!important;
  border:2px solid {NAV_BOR}!important;background:{'rgba(255,255,255,.04)' if IS_DARK else G100}!important;
  color:{TEXT2}!important;box-shadow:none!important;
}}
[data-testid="column"]:first-of-type [data-testid="stColumns"] .stButton>button:hover {{
  background:{ACC}!important;color:{BLACK}!important;border-color:{ACC}!important;
}}
[data-testid="column"]:first-of-type [data-testid="stColumns"] .stButton>button[kind="primary"] {{
  background:{BLACK if not IS_DARK else WHITE}!important;
  color:{WHITE if not IS_DARK else BLACK}!important;
  border:2px solid {BLACK if not IS_DARK else WHITE}!important;
  font-weight:700!important;
}}
[data-testid="column"]:first-of-type [data-testid="stColumns"] .stButton>button[kind="primary"]:hover {{
  background:{BLACK if not IS_DARK else WHITE}!important;transform:none!important;
}}

/* Logout button */
[data-testid="column"]:first-of-type .stButton>button:last-of-type:not([kind="primary"]) {{
  border-color:{'rgba(255,255,255,.1)' if IS_DARK else G200}!important;
}}

[data-testid="column"]:first-of-type hr {{
  border:none!important;
  border-top:2px solid {NAV_BOR}!important;
  margin:.75rem 0!important;
}}
</style>""", unsafe_allow_html=True)

nav_col, content_col = st.columns([1, 4], gap="small")

with nav_col:
    # Logo — portfolio nav-logo style
    st.markdown(f"""<div style="padding:1.25rem .875rem 1rem;
      border-bottom:2px solid {NAV_BOR};margin-bottom:.875rem;">
      <div style="display:flex;align-items:center;gap:.75rem;">
        <div style="width:40px;height:40px;background:{ACC};color:{BLACK};
          display:flex;align-items:center;justify-content:center;
          border:2px solid {NAV_BOR};box-shadow:{SHADOW_SM};
          font-size:1.2rem;flex-shrink:0;">🛡️</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:.95rem;
            color:{TEXT};letter-spacing:-.02em;">AgentFlow</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:.55rem;
            color:{TEXT3};letter-spacing:.1em;text-transform:uppercase;">Finance Guard</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # User card — stats-grid style from portfolio
    st.markdown(f"""<div style="margin:0 .75rem .875rem;
      border:2px solid {NAV_BOR};box-shadow:{SHADOW_SM};">
      <div style="background:{ACC};padding:.6rem .875rem;display:flex;align-items:center;gap:.6rem;">
        <div style="width:28px;height:28px;background:{BLACK};color:{WHITE};
          display:flex;align-items:center;justify-content:center;
          font-family:'Syne',sans-serif;font-weight:800;font-size:.7rem;flex-shrink:0;">
          {nm[0].upper() if nm else 'U'}
        </div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:.8rem;color:{BLACK};line-height:1.2;">{nm}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:rgba(0,0,0,0.6);">{rl.lower()}</div>
        </div>
      </div>
      <div style="background:{'#111' if IS_DARK else G100};padding:.5rem .875rem;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:{TEXT3};word-break:break-all;">{em}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Nav label
    st.markdown(f"""<div style="padding:0 .875rem .35rem;font-family:'JetBrains Mono',monospace;
      font-size:.58rem;font-weight:500;color:{TEXT3};text-transform:uppercase;letter-spacing:.12em;">{t('navigation')}</div>""",
      unsafe_allow_html=True)

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

    # Theme + Language
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

    st.markdown(f"""<div style="text-align:center;font-family:'JetBrains Mono',monospace;
      color:{TEXT3};font-size:.55rem;padding:.75rem 0 .5rem;border-top:2px solid {NAV_BOR};
      margin-top:.5rem;">v{config.APP_VERSION}</div>""", unsafe_allow_html=True)

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
