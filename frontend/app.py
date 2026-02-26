"""AgentFlow Finance Guard — SPA with custom nav column."""
import sys, logging, importlib
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import config
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title=config.APP_NAME, page_icon="🛡️", layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": f"{config.APP_NAME} v{config.APP_VERSION}"},
)

# Defaults
for k, v in {"logged_in":False,"user_email":"","user_name":"","user_role":"viewer",
              "access_token":"","theme":"dark","page":"Overview","show_logout_confirm":False}.items():
    if k not in st.session_state: st.session_state[k] = v

IS_DARK = st.session_state.theme == "dark"

# Load theme
try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    st.markdown(DARK_THEME if IS_DARK else LIGHT_THEME, unsafe_allow_html=True)
except Exception: pass

# Kill native Streamlit sidebar/toolbar
st.markdown("""<style>
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important;}
</style>""", unsafe_allow_html=True)

# ── LOGIN ────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback; st.error(f"Login error: {e}"); st.code(traceback.format_exc())
    st.stop()

# ── LOGGED IN ────────────────────────────────────────────────────
IS_DARK = st.session_state.theme == "dark"
NAV_TEXT  = "#e2e8f0" if IS_DARK else "#0f172a"
NAV_TEXT2 = "#64748b"
NAV_BOR   = "rgba(59,130,246,0.2)" if IS_DARK else "rgba(0,0,0,0.08)"
ACTIVE_BG = "rgba(59,130,246,0.15)" if IS_DARK else "rgba(37,99,235,0.08)"
ACTIVE_C  = "#3b82f6" if IS_DARK else "#2563eb"

nm = st.session_state.user_name or "User"
rl = (st.session_state.user_role or "viewer").title()
em = st.session_state.user_email or ""
rc = {"Admin":"#3b82f6","Analyst":"#10b981","Viewer":"#f59e0b"}.get(rl, "#94a3b8")

PAGES = [
    ("Overview","📊"),("Upload","📄"),("Fraud","🚨"),
    ("ML Insights","🧠"),("Security","🛡️"),("Observability","📈"),
    ("Merchant","💼"),("Integrations","🔗"),("Settings","⚙️"),
]
PAGE_KEY = {p[0]: p[0].replace(" ","_") for p in PAGES}
MOD_MAP  = {
    "Overview":"page_overview","Upload":"page_upload","Fraud":"page_fraud",
    "ML_Insights":"page_ml","Security":"page_security","Observability":"page_observability",
    "Merchant":"page_merchant","Integrations":"page_integrations","Settings":"page_settings",
}

nav_col, content_col = st.columns([1, 4], gap="small")

# ── NAV ──────────────────────────────────────────────────────────
with nav_col:
    # Logo area
    st.markdown(f"""
<div style="padding:1.75rem 1rem 1.25rem;text-align:center;border-bottom:1px solid {NAV_BOR};">
  <div style="font-size:2.2rem;filter:drop-shadow(0 0 16px rgba(59,130,246,0.55));">🛡️</div>
  <div style="font-size:1.05rem;font-weight:700;letter-spacing:-.01em;margin-top:6px;
    background:linear-gradient(135deg,#3b82f6,#06b6d4);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    AgentFlow</div>
  <div style="font-size:0.6rem;color:{NAV_TEXT2};text-transform:uppercase;letter-spacing:.12em;margin-top:2px;">
    Finance Guard</div>
</div>""", unsafe_allow_html=True)

    # User card
    st.markdown(f"""
<div style="margin:1rem 0.75rem 0.5rem;padding:0.75rem;
  background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.15);border-radius:10px;">
  <div style="font-weight:600;font-size:0.875rem;color:{NAV_TEXT};">{nm}</div>
  <div style="font-size:0.7rem;color:{rc};font-weight:600;margin-top:2px;">{rl}</div>
  <div style="font-size:0.65rem;color:{NAV_TEXT2};margin-top:1px;word-break:break-all;">{em}</div>
</div>""", unsafe_allow_html=True)

    # Nav label
    st.markdown(f"""<div style="padding:0.5rem 1rem 0.25rem;
      font-size:0.62rem;font-weight:600;color:{NAV_TEXT2};
      text-transform:uppercase;letter-spacing:.1em;">Navigation</div>""",
      unsafe_allow_html=True)

    # Nav buttons
    for pname, icon in PAGES:
        pkey = PAGE_KEY[pname]
        is_active = st.session_state.page == pkey
        if st.button(f"{icon}  {pname}", key=f"nav_{pkey}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pkey; st.rerun()

    # Bottom controls
    st.markdown('<div style="margin-top:auto;padding-top:0.5rem;"></div>', unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️", use_container_width=True, key="th_l", help="Light mode",
                     type="primary" if not IS_DARK else "secondary"):
            st.session_state.theme = "light"; st.rerun()
    with c2:
        if st.button("🌙", use_container_width=True, key="th_d", help="Dark mode",
                     type="primary" if IS_DARK else "secondary"):
            st.session_state.theme = "dark"; st.rerun()

    st.markdown('<div style="height:0.25rem;"></div>', unsafe_allow_html=True)

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

    st.markdown(f'<div style="text-align:center;color:{NAV_TEXT2};font-size:.6rem;padding:.75rem 0 .5rem;">v{config.APP_VERSION}</div>',
                unsafe_allow_html=True)

# ── PAGE CONTENT ─────────────────────────────────────────────────
with content_col:
    st.markdown('<div style="padding:2.25rem 2.75rem 5rem;">', unsafe_allow_html=True)
    page_key = st.session_state.page
    mod_name = MOD_MAP.get(page_key, "page_overview")
    try:
        mod = importlib.import_module(f"pages.{mod_name}")
        mod.render()
    except Exception as e:
        import traceback
        st.error(f"Page error on '{page_key}': {e}")
        st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)
