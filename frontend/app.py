"""AgentFlow Finance Guard - True SPA."""
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

try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    st.markdown(DARK_THEME if st.session_state.theme=="dark" else LIGHT_THEME, unsafe_allow_html=True)
except Exception: pass

# ── LOGIN PAGE ───────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""<style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    .main .block-container{max-width:100%!important;padding:0!important;}
    </style>""", unsafe_allow_html=True)
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback
        st.error(f"Login error: {e}")
        st.code(traceback.format_exc())
    st.stop()

# ── SIDEBAR ──────────────────────────────────────────────────────
PAGES = [
    ("Overview",      "📊", ["admin","analyst","viewer"]),
    ("Upload",        "📄", ["admin","analyst"]),
    ("Fraud",         "🚨", ["admin","analyst"]),
    ("ML_Insights",   "🧠", ["admin","analyst"]),
    ("Security",      "🛡️", ["admin"]),
    ("Observability", "📈", ["admin","analyst"]),
    ("Merchant",      "💼", ["admin","analyst","viewer"]),
    ("Integrations",  "🔗", ["admin"]),
    ("Settings",      "⚙️", ["admin","analyst","viewer"]),
]

with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:1.5rem 0 1rem;">'
        '<div style="font-size:2.5rem;">🛡️</div>'
        '<div style="font-size:1.2rem;font-weight:800;'
        'background:linear-gradient(135deg,#3b82f6,#06b6d4);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'background-clip:text;font-family:sans-serif;">AgentFlow</div>'
        '<div style="font-size:0.68rem;opacity:0.45;text-transform:uppercase;letter-spacing:.1em;">'
        'Finance Guard</div></div>', unsafe_allow_html=True)
    st.divider()

    nm = st.session_state.user_name or "User"
    rl = (st.session_state.user_role or "viewer").title()
    em = st.session_state.user_email or ""
    rc = {"Admin":"#3b82f6","Analyst":"#10b981","Viewer":"#f59e0b"}.get(rl,"#94a3b8")
    st.markdown(
        f'<div style="padding:.65rem;background:rgba(59,130,246,.08);border-radius:10px;'
        f'border:1px solid rgba(59,130,246,.15);margin-bottom:.75rem;">'
        f'<div style="font-weight:600;font-size:.9rem;">{nm}</div>'
        f'<div style="font-size:.72rem;color:{rc};font-weight:600;">{rl}</div>'
        f'<div style="font-size:.68rem;opacity:.45;">{em}</div></div>',
        unsafe_allow_html=True)

    role_lower = (st.session_state.user_role or "viewer").lower()
    for pname, icon, roles in PAGES:
        if role_lower not in roles: continue
        is_active = st.session_state.page == pname
        label = f"{icon}  {pname.replace('_',' ')}"
        if st.button(label, key=f"nav_{pname}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pname; st.rerun()

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        if st.button("☀️",use_container_width=True,key="th_l",help="Light",
                     type="primary" if st.session_state.theme=="light" else "secondary"):
            st.session_state.theme="light"; st.rerun()
    with c2:
        if st.button("🌙",use_container_width=True,key="th_d",help="Dark",
                     type="primary" if st.session_state.theme=="dark" else "secondary"):
            st.session_state.theme="dark"; st.rerun()
    st.divider()
    if not st.session_state.show_logout_confirm:
        if st.button("🚪 Logout",use_container_width=True,key="lo_btn"):
            st.session_state.show_logout_confirm=True; st.rerun()
    else:
        st.warning("Confirm logout?")
        a,b=st.columns(2)
        with a:
            if st.button("Yes",type="primary",use_container_width=True,key="lo_y"):
                for k in ["logged_in","user_email","user_name","user_role","access_token"]:
                    st.session_state[k]=False if k=="logged_in" else ""
                st.session_state.page="Overview"; st.session_state.show_logout_confirm=False; st.rerun()
        with b:
            if st.button("No",use_container_width=True,key="lo_n"):
                st.session_state.show_logout_confirm=False; st.rerun()
    st.markdown(f'<div style="text-align:center;opacity:.25;font-size:.65rem;padding-top:.4rem;">v{config.APP_VERSION}</div>',unsafe_allow_html=True)

# ── PAGE ROUTING ─────────────────────────────────────────────────
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
