"""AgentFlow Finance Guard - True SPA, custom sidebar via columns."""
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

_defaults = {"logged_in":False,"user_email":"","user_name":"","user_role":"viewer",
             "access_token":"","theme":"dark","page":"Overview","show_logout_confirm":False,
             "nav_open":True}
for k,v in _defaults.items():
    if k not in st.session_state: st.session_state[k] = v

try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    st.markdown(DARK_THEME if st.session_state.theme=="dark" else LIGHT_THEME,
                unsafe_allow_html=True)
except Exception: pass

# ── CUSTOM NAV CSS ───────────────────────────────────────────────
st.markdown("""<style>
/* Hide Streamlit native sidebar entirely */
[data-testid="stSidebar"]{display:none!important;}
[data-testid="collapsedControl"]{display:none!important;}

/* Remove default padding so our layout fills full width */
.main .block-container{
    padding:0 !important;
    max-width:100% !important;
}
/* Nav column styling */
.nav-col {
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    background: var(--bg2, #0c1020);
    border-right: 1px solid var(--border, rgba(59,130,246,0.15));
    padding: 0;
}
/* Outer row: remove gaps */
div[data-testid="stHorizontalBlock"] > div:first-child {
    padding-right: 0 !important;
}
</style>""", unsafe_allow_html=True)

# ── LOGIN PAGE ───────────────────────────────────────────────────
if not st.session_state.logged_in:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback
        st.error(f"Login error: {e}")
        st.code(traceback.format_exc())
    st.stop()

# ── LAYOUT: custom nav column + content column ───────────────────
PAGES = [
    ("Overview",      "📊"),
    ("Upload",        "📄"),
    ("Fraud",         "🚨"),
    ("ML_Insights",   "🧠"),
    ("Security",      "🛡️"),
    ("Observability", "📈"),
    ("Merchant",      "💼"),
    ("Integrations",  "🔗"),
    ("Settings",      "⚙️"),
]

IS_DARK = st.session_state.theme == "dark"
NAV_BG   = "#0c1020" if IS_DARK else "#ffffff"
NAV_BOR  = "rgba(59,130,246,0.15)" if IS_DARK else "rgba(37,99,235,0.10)"
TEXT_COL = "#e2e8f0" if IS_DARK else "#0f172a"
TEXT2    = "#94a3b8" if IS_DARK else "#475569"
ACTIVE_BG = "rgba(59,130,246,0.18)" if IS_DARK else "rgba(37,99,235,0.10)"
ACTIVE_BOR = "#3b82f6" if IS_DARK else "#2563eb"
HOVER_BG  = "rgba(59,130,246,0.08)" if IS_DARK else "rgba(37,99,235,0.05)"

# Full-width outer container with nav + content
nav_col, content_col = st.columns([1, 4], gap="small")

with nav_col:
    st.markdown(f"""
<div style="
    background:{NAV_BG};
    border-right:1px solid {NAV_BOR};
    min-height:100vh;
    padding:1.5rem 0.75rem 1rem;
    display:flex;
    flex-direction:column;
    gap:0.25rem;
    position:sticky;
    top:0;
">
    <!-- Logo -->
    <div style="text-align:center;padding-bottom:1.25rem;border-bottom:1px solid {NAV_BOR};margin-bottom:0.75rem;">
        <div style="font-size:2.2rem;filter:drop-shadow(0 0 10px rgba(59,130,246,0.5));">🛡️</div>
        <div style="font-size:1.1rem;font-weight:700;
            background:linear-gradient(135deg,#3b82f6,#06b6d4);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;letter-spacing:-0.01em;">AgentFlow</div>
        <div style="font-size:0.6rem;color:{TEXT2};text-transform:uppercase;letter-spacing:.12em;">Finance Guard</div>
    </div>
</div>
""", unsafe_allow_html=True)

    # User info
    nm = st.session_state.user_name or "User"
    rl = (st.session_state.user_role or "viewer").title()
    em = st.session_state.user_email or ""
    rc = {"Admin":"#3b82f6","Analyst":"#10b981","Viewer":"#f59e0b"}.get(rl,"#94a3b8")
    st.markdown(f"""
<div style="background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.15);
    border-radius:10px;padding:0.6rem 0.75rem;margin-bottom:0.75rem;">
    <div style="font-weight:600;font-size:0.88rem;color:{TEXT_COL};">{nm}</div>
    <div style="font-size:0.7rem;color:{rc};font-weight:600;">{rl}</div>
    <div style="font-size:0.65rem;color:{TEXT2};margin-top:1px;">{em}</div>
</div>""", unsafe_allow_html=True)

    # Nav buttons
    for pname, icon in PAGES:
        is_active = st.session_state.page == pname
        label = f"{icon}  {pname.replace('_',' ')}"
        if st.button(label, key=f"nav_{pname}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pname
            st.rerun()

    st.divider()

    # Theme toggle
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️", use_container_width=True, key="th_l",
                     type="primary" if not IS_DARK else "secondary"):
            st.session_state.theme = "light"; st.rerun()
    with c2:
        if st.button("🌙", use_container_width=True, key="th_d",
                     type="primary" if IS_DARK else "secondary"):
            st.session_state.theme = "dark"; st.rerun()

    st.divider()

    # Logout
    if not st.session_state.show_logout_confirm:
        if st.button("🚪 Logout", use_container_width=True, key="lo_btn"):
            st.session_state.show_logout_confirm = True; st.rerun()
    else:
        st.warning("Confirm?")
        a, b = st.columns(2)
        with a:
            if st.button("Yes", type="primary", use_container_width=True, key="lo_y"):
                for k in ["logged_in","user_email","user_name","user_role","access_token"]:
                    st.session_state[k] = False if k=="logged_in" else ""
                st.session_state.page = "Overview"
                st.session_state.show_logout_confirm = False
                st.rerun()
        with b:
            if st.button("No", use_container_width=True, key="lo_n"):
                st.session_state.show_logout_confirm = False; st.rerun()

    st.markdown(f'<div style="text-align:center;color:{TEXT2};font-size:.6rem;padding-top:.5rem;">v{config.APP_VERSION}</div>',
                unsafe_allow_html=True)

# ── PAGE CONTENT ─────────────────────────────────────────────────
with content_col:
    # Add padding inside content
    st.markdown('<div style="padding:1.75rem 2rem 2rem;">', unsafe_allow_html=True)
    MOD = {
        "Overview":"page_overview","Upload":"page_upload","Fraud":"page_fraud",
        "ML_Insights":"page_ml","Security":"page_security","Observability":"page_observability",
        "Merchant":"page_merchant","Integrations":"page_integrations","Settings":"page_settings",
    }
    mod_name = MOD.get(st.session_state.page, "page_overview")
    try:
        mod = importlib.import_module(f"pages.{mod_name}")
        mod.render()
    except Exception as e:
        import traceback
        st.error(f"Page error: {e}")
        st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)
