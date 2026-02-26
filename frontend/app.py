"""AgentFlow Finance Guard - True SPA with custom column nav."""
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
             "access_token":"","theme":"dark","page":"Overview","show_logout_confirm":False}
for k,v in _defaults.items():
    if k not in st.session_state: st.session_state[k] = v

IS_DARK = st.session_state.theme == "dark"

try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    st.markdown(DARK_THEME if IS_DARK else LIGHT_THEME, unsafe_allow_html=True)
except Exception: pass

# Kill ALL Streamlit chrome - sidebar, toolbar, padding
st.markdown("""<style>
[data-testid="stSidebar"]{display:none!important;}
[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
#MainMenu{display:none!important;}
footer{display:none!important;}
header{display:none!important;}
.main .block-container{
    padding:0!important;
    max-width:100%!important;
    margin:0!important;
}
/* Remove gap between columns */
[data-testid="stHorizontalBlock"]{gap:0!important;}
[data-testid="stHorizontalBlock"] > div{padding:0!important;}
</style>""", unsafe_allow_html=True)

# ── LOGIN ────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback
        st.error(f"Login error: {e}")
        st.code(traceback.format_exc())
    st.stop()

# ── LOGGED IN LAYOUT ─────────────────────────────────────────────
IS_DARK = st.session_state.theme == "dark"
NAV_BG    = "#0b0f1c" if IS_DARK else "#ffffff"
NAV_BOR   = "rgba(59,130,246,0.2)" if IS_DARK else "rgba(37,99,235,0.1)"
TEXT      = "#e2e8f0" if IS_DARK else "#0f172a"
TEXT2     = "#64748b" if IS_DARK else "#64748b"
CONT_BG   = "#060912" if IS_DARK else "#f0f4ff"

PAGES = [
    ("Overview","📊"),("Upload","📄"),("Fraud","🚨"),
    ("ML_Insights","🧠"),("Security","🛡️"),("Observability","📈"),
    ("Merchant","💼"),("Integrations","🔗"),("Settings","⚙️"),
]

nav_col, content_col = st.columns([1, 4], gap="small")

# ── NAV COLUMN ───────────────────────────────────────────────────
with nav_col:
    nm = st.session_state.user_name or "User"
    rl = (st.session_state.user_role or "viewer").title()
    em = st.session_state.user_email or ""
    rc = {"Admin":"#3b82f6","Analyst":"#10b981","Viewer":"#f59e0b"}.get(rl,"#94a3b8")

    st.markdown(f"""<style>
    /* Nav column full height flush */
    [data-testid="stHorizontalBlock"] > div:first-child > div {{
        background: {NAV_BG};
        min-height: 100vh;
        border-right: 1px solid {NAV_BOR};
        position: sticky;
        top: 0;
    }}
    /* Content column background */
    [data-testid="stHorizontalBlock"] > div:last-child > div {{
        background: {CONT_BG};
        min-height: 100vh;
    }}
    </style>
    <div style="padding:1.5rem 0.85rem 1rem;display:flex;flex-direction:column;gap:0.15rem;">
        <div style="text-align:center;padding-bottom:1.2rem;
            border-bottom:1px solid {NAV_BOR};margin-bottom:0.9rem;">
            <div style="font-size:2rem;filter:drop-shadow(0 0 14px rgba(59,130,246,0.7));">🛡️</div>
            <div style="font-size:1.05rem;font-weight:700;letter-spacing:-.01em;
                background:linear-gradient(135deg,#3b82f6,#06b6d4);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;margin-top:4px;">AgentFlow</div>
            <div style="font-size:0.58rem;color:{TEXT2};text-transform:uppercase;
                letter-spacing:.12em;margin-top:2px;">Finance Guard</div>
        </div>
        <div style="background:rgba(59,130,246,.07);border:1px solid rgba(59,130,246,.15);
            border-radius:10px;padding:0.6rem 0.75rem;margin-bottom:0.75rem;">
            <div style="font-weight:600;font-size:0.85rem;color:{TEXT};">{nm}</div>
            <div style="font-size:0.68rem;color:{rc};font-weight:600;margin-top:1px;">{rl}</div>
            <div style="font-size:0.62rem;color:{TEXT2};margin-top:1px;word-break:break-all;">{em}</div>
        </div>
        <div style="font-size:0.62rem;color:{TEXT2};text-transform:uppercase;
            letter-spacing:.1em;padding:0 0.25rem 0.4rem;font-weight:600;">Navigation</div>
    </div>""", unsafe_allow_html=True)

    for pname, icon in PAGES:
        is_active = st.session_state.page == pname
        label = f"{icon}  {pname.replace('_',' ')}"
        if st.button(label, key=f"nav_{pname}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pname; st.rerun()

    st.markdown('<div style="margin-top:0.5rem;"></div>', unsafe_allow_html=True)
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

    st.markdown('<div style="margin-top:0.25rem;"></div>', unsafe_allow_html=True)

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
                st.session_state.show_logout_confirm = False; st.rerun()
        with b:
            if st.button("No", use_container_width=True, key="lo_n"):
                st.session_state.show_logout_confirm = False; st.rerun()

    st.markdown(f'<div style="text-align:center;color:{TEXT2};font-size:.58rem;'
                f'padding:0.75rem 0 0.5rem;">v{config.APP_VERSION}</div>',
                unsafe_allow_html=True)

# ── CONTENT COLUMN ───────────────────────────────────────────────
with content_col:
    st.markdown('<div style="padding:2rem 2.25rem 3rem;">', unsafe_allow_html=True)
    MOD = {
        "Overview":"page_overview","Upload":"page_upload","Fraud":"page_fraud",
        "ML_Insights":"page_ml","Security":"page_security","Observability":"page_observability",
        "Merchant":"page_merchant","Integrations":"page_integrations","Settings":"page_settings",
    }
    try:
        mod = importlib.import_module(f"pages.{MOD.get(st.session_state.page,'page_overview')}")
        mod.render()
    except Exception as e:
        import traceback
        st.error(f"Page error: {e}")
        st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)
