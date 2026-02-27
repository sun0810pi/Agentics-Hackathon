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

# Load theme FIRST - before anything else
try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    st.markdown(DARK_THEME if IS_DARK else LIGHT_THEME, unsafe_allow_html=True)
except Exception: pass

# ── JS: Remove all top/left padding dynamically (works on all Streamlit versions) ──
st.markdown("""<style>
/* Ultra-aggressive padding removal */
section[data-testid="stMain"] > div,
div[data-testid="stVerticalBlock"],
div[data-testid="stAppViewBlockContainer"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
/* Remove Streamlit's default 6rem top padding */
.css-1y4p8pa, .css-z5fcl4, .css-ocqkz7,
.css-1544g2n, .css-zt5igj, .e1tzin5v3,
div.block-container { 
    padding-top: 0 !important; 
    padding-left: 0 !important;
    margin-top: 0 !important;
}
/* Target the actual app view container gap */
[data-testid="stAppViewContainer"] {
    padding: 0 !important;
}
/* Nuke the scrollable container padding */
[data-testid="ScrollToBottomContainer"] > div {
    padding: 0 !important;
}
</style>""", unsafe_allow_html=True)

# ── LOGIN ────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback; st.error(f"Login error: {e}"); st.code(traceback.format_exc())
    st.stop()

# ── LOGGED IN LAYOUT ─────────────────────────────────────────────
IS_DARK   = st.session_state.theme == "dark"
NAV_TEXT  = "#f1f5f9" if IS_DARK else "#0f172a"
NAV_TEXT2 = "#64748b"
NAV_BOR   = "rgba(59,130,246,0.22)" if IS_DARK else "rgba(0,0,0,0.09)"
ROLE_CLR  = {"Admin":"#3b82f6","Analyst":"#10b981","Viewer":"#f59e0b"}

nm = st.session_state.user_name or "User"
rl = (st.session_state.user_role or "viewer").title()
em = st.session_state.user_email or ""
rc = ROLE_CLR.get(rl, "#94a3b8")

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

nav_col, content_col = st.columns([1, 4], gap="small")

with nav_col:
    st.markdown(f"""<div style="padding:1.75rem 0.875rem 1.25rem;text-align:center;
      border-bottom:1px solid {NAV_BOR};margin-bottom:0.875rem;">
      <div style="font-size:2.2rem;filter:drop-shadow(0 0 16px rgba(59,130,246,0.55));">🛡️</div>
      <div style="font-size:1.05rem;font-weight:700;margin-top:6px;
        background:linear-gradient(135deg,#3b82f6,#06b6d4);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
        AgentFlow</div>
      <div style="font-size:0.58rem;color:{NAV_TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-top:2px;">
        Finance Guard</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="margin:0 0.625rem 0.875rem;padding:0.75rem 0.875rem;
      background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.15);border-radius:10px;">
      <div style="font-weight:600;font-size:0.875rem;color:{NAV_TEXT};">{nm}</div>
      <div style="font-size:0.7rem;color:{rc};font-weight:600;margin-top:2px;">{rl}</div>
      <div style="font-size:0.62rem;color:{NAV_TEXT2};margin-top:1px;word-break:break-all;">{em}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="padding:0 0.875rem 0.375rem;font-size:0.6rem;font-weight:600;
      color:{NAV_TEXT2};text-transform:uppercase;letter-spacing:.1em;">Navigation</div>""",
      unsafe_allow_html=True)

    for pname, icon in PAGES:
        pkey = PAGE_KEY[pname]
        is_active = st.session_state.page == pkey
        if st.button(f"{icon}  {pname}", key=f"nav_{pkey}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pkey; st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️", use_container_width=True, key="th_l",
                     type="primary" if not IS_DARK else "secondary"):
            st.session_state.theme = "light"; st.rerun()
    with c2:
        if st.button("🌙", use_container_width=True, key="th_d",
                     type="primary" if IS_DARK else "secondary"):
            st.session_state.theme = "dark"; st.rerun()

    st.markdown('<div style="height:.25rem"></div>', unsafe_allow_html=True)

    if not st.session_state.show_logout_confirm:
        if st.button("🚪 Logout", use_container_width=True, key="lo_btn"):
            st.session_state.show_logout_confirm = True; st.rerun()
    else:
        st.warning("Confirm logout?")
        a, b = st.columns(2)
        with a:
            if st.button("Yes", type="primary", use_container_width=True, key="lo_y"):
                for k in ["logged_in","user_email","user_name","user_role","access_token"]:
                    st.session_state[k] = False if k=="logged_in" else ""
                st.session_state.page = "Overview"
                st.session_state.show_logout_confirm = False; st.rerun()
        with b:
            if st.button("No", use_container_width=True, key="lo_n"):
                st.session_state.show_logout_confirm = False; st.rerun()

    st.markdown(f'<div style="text-align:center;color:{NAV_TEXT2};font-size:.58rem;padding:.75rem 0 .5rem;">v{config.APP_VERSION}</div>',
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
