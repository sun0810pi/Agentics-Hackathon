"""AgentFlow Finance Guard - True SPA, zero multipage routing."""
import sys, logging
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import config
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": f"{config.APP_NAME} v{config.APP_VERSION}"},
)

# ── Session state ────────────────────────────────────────────────
_defaults = {
    "logged_in": False, "user_email": "", "user_name": "",
    "user_role": "viewer", "access_token": "", "theme": "dark",
    "page": "Overview", "show_logout_confirm": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Theme ────────────────────────────────────────────────────────
try:
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    _css = DARK_THEME if st.session_state.theme == "dark" else LIGHT_THEME
    st.markdown(_css, unsafe_allow_html=True)
except Exception as e:
    pass  # Theme fail is non-fatal

# ── Login page ───────────────────────────────────────────────────
if not st.session_state.logged_in:
    try:
        from auth.login import login_page
        login_page()
    except Exception as e:
        import traceback
        st.error(f"Login error: {e}")
        st.code(traceback.format_exc())
    st.stop()

# ══════════════════════════════════════════════════════════════════
# LOGGED IN — render sidebar + current page
# ══════════════════════════════════════════════════════════════════

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

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:1rem 0;">'
        '<div style="font-size:2.5rem;">🛡️</div>'
        '<div style="font-size:1.2rem;font-weight:900;color:#4A9EFF;">AgentFlow</div>'
        '<div style="opacity:0.6;font-size:0.8rem;">Finance Guard</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.divider()

    nm = st.session_state.user_name or "User"
    rl = (st.session_state.user_role or "viewer").title()
    em = st.session_state.user_email or ""
    rc = {"Admin":"#4A9EFF","Analyst":"#00d68f","Viewer":"#ffab00"}.get(rl, "#718096")
    st.markdown(
        f'<div style="padding:0.6rem;background:rgba(74,158,255,0.1);'
        f'border-radius:8px;border:1px solid rgba(74,158,255,0.2);margin-bottom:0.75rem;">'
        f'<b>{nm}</b><br/>'
        f'<span style="font-size:0.72rem;color:{rc};font-weight:700;">{rl}</span><br/>'
        f'<span style="font-size:0.68rem;opacity:0.55;">{em}</span></div>',
        unsafe_allow_html=True
    )

    st.markdown("**Navigation**")
    role = (st.session_state.user_role or "viewer").lower()
    for pname, icon, roles in PAGES:
        if role not in roles:
            continue
        label = f"{icon} {pname.replace('_',' ')}"
        is_active = st.session_state.page == pname
        if st.button(label, key=f"nav_{pname}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = pname
            st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☀️ Light", use_container_width=True,
                     type="primary" if st.session_state.theme=="light" else "secondary",
                     key="th_l"):
            st.session_state.theme = "light"; st.rerun()
    with c2:
        if st.button("🌙 Dark", use_container_width=True,
                     type="primary" if st.session_state.theme=="dark" else "secondary",
                     key="th_d"):
            st.session_state.theme = "dark"; st.rerun()

    st.divider()
    if not st.session_state.show_logout_confirm:
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.show_logout_confirm = True; st.rerun()
    else:
        st.warning("Logout?")
        a, b = st.columns(2)
        with a:
            if st.button("✅ Yes", type="primary", use_container_width=True, key="lo_yes"):
                for k in ["logged_in","user_email","user_name","user_role","access_token"]:
                    st.session_state[k] = False if k == "logged_in" else ""
                st.session_state.page = "Overview"
                st.session_state.show_logout_confirm = False
                st.rerun()
        with b:
            if st.button("❌ No", use_container_width=True, key="lo_no"):
                st.session_state.show_logout_confirm = False; st.rerun()

# ── Page routing ─────────────────────────────────────────────────
page = st.session_state.page

try:
    if page == "Overview":
        from pages.page_overview import render
        render()
    elif page == "Upload":
        from pages.page_upload import render
        render()
    elif page == "Fraud":
        from pages.page_fraud import render
        render()
    elif page == "ML_Insights":
        from pages.page_ml import render
        render()
    elif page == "Security":
        from pages.page_security import render
        render()
    elif page == "Observability":
        from pages.page_observability import render
        render()
    elif page == "Merchant":
        from pages.page_merchant import render
        render()
    elif page == "Integrations":
        from pages.page_integrations import render
        render()
    elif page == "Settings":
        from pages.page_settings import render
        render()
    else:
        st.error(f"Unknown page: {page}")
except Exception as e:
    import traceback
    st.error(f"❌ Error loading page '{page}': {e}")
    st.code(traceback.format_exc())
