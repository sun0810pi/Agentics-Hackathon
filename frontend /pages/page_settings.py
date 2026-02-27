import streamlit as st
from i18n import t
from components.ui_helpers import page_header, spacer as sp, is_dark

def section_card(title, icon, dark=None):
    D   = is_dark() if dark is None else dark
    BG  = '#141414' if D else '#ffffff'
    BOR = '#262626' if D else '#e5e0da'
    T   = '#f5f5f5' if D else '#0a0a0a'
    st.markdown(f'''<div style="background:{BG};border:2px solid {BOR};border-radius:12px;
padding:1.1rem 1.25rem .25rem;margin-bottom:.75rem;position:relative;overflow:hidden;
box-shadow:3px 3px 0px {'rgba(0,0,0,.35)' if D else 'rgba(0,0,0,.06)'};">
<div style="position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#10b981,#34d399);"></div>
<div style="font-family:'Syne',sans-serif;font-size:.88rem;font-weight:700;
  color:{T};margin-bottom:.75rem;">{icon} {title}</div>
''', unsafe_allow_html=True)

def render():
    import logging
    logger = logging.getLogger(__name__)

    IS_DARK = st.session_state.get('theme','dark') == 'dark'
    D   = IS_DARK
    T   = '#f1f5f9' if D else '#0f172a'
    T2  = '#94a3b8' if D else '#64748b'
    BOR = 'rgba(59,130,246,0.13)' if D else 'rgba(0,0,0,0.07)'
    lang = st.session_state.get('language','en')

    page_header("⚙️", t("settings"), "App configuration & preferences")

    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🎨 Appearance", "🔔 Notifications", "🔐 Security"])

    # ── Profile tab ──────────────────────────────────────────────
    with tab1:
        sp(".5rem")
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">User Information</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", value=st.session_state.get('user_name',''))
            email = st.text_input("Email", value=st.session_state.get('user_email',''), disabled=True)
        with c2:
            role = st.session_state.get('user_role','viewer').title()
            st.markdown(f'<div style="font-size:.72rem;color:{T2};text-transform:uppercase;font-weight:600;margin-bottom:.3rem;">Role</div><div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);border-radius:8px;padding:.65rem 1rem;font-size:.9rem;font-weight:600;color:#60a5fa;">{role}</div>', unsafe_allow_html=True)
            dept = st.text_input("Department", value="Finance Security")

        sp(".5rem")
        if st.button("💾 Save Profile", type="primary"):
            if name: st.session_state.user_name = name
            st.success("✅ Profile updated successfully!")

        sp(".75rem")
        st.markdown(f'<hr style="border:none;border-top:1px solid {BOR};margin:.5rem 0 1rem;">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">Danger Zone</div>', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", type="secondary"):
            for k in ["logged_in","user_email","user_name","user_role","access_token"]:
                st.session_state[k] = False if k=="logged_in" else ""
            st.session_state.page = "Overview"
            st.rerun()

    # ── Appearance tab ───────────────────────────────────────────
    with tab2:
        sp(".5rem")

        # Theme
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🌓 {t("theme")}</div>', unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns([1,1,2])
        with tc1:
            if st.button(f"🌙 {t('dark_mode')}", type="primary" if D else "secondary", use_container_width=True):
                st.session_state.theme = "dark"; st.rerun()
        with tc2:
            if st.button(f"☀️ {t('light_mode')}", type="primary" if not D else "secondary", use_container_width=True):
                st.session_state.theme = "light"; st.rerun()

        sp("1rem")

        # Language
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🌐 {t("language")}</div>', unsafe_allow_html=True)
        lc1, lc2, lc3 = st.columns([1,1,2])
        with lc1:
            if st.button("🇬🇧 English", type="primary" if lang=="en" else "secondary", use_container_width=True):
                st.session_state.language = "en"; st.rerun()
        with lc2:
            if st.button("🇻🇳 Tiếng Việt", type="primary" if lang=="vi" else "secondary", use_container_width=True):
                st.session_state.language = "vi"; st.rerun()

        sp("1rem")

        # Display
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">👁️ Display Options</div>', unsafe_allow_html=True)
        compact = st.toggle("Compact mode", value=False)
        animations = st.toggle("Enable animations", value=True)
        if st.button("💾 Save Display Settings", type="primary"):
            st.success("✅ Display settings saved!")

    # ── Notifications tab ────────────────────────────────────────
    with tab3:
        sp(".5rem")
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">📧 Email Notifications</div>', unsafe_allow_html=True)
        st.toggle("High-risk fraud alerts", value=True)
        st.toggle("Daily summary report", value=True)
        st.toggle("Weekly analytics digest", value=False)
        st.toggle("System downtime alerts", value=True)

        sp(".75rem")
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🔔 In-App Notifications</div>', unsafe_allow_html=True)
        st.toggle("Real-time fraud alerts", value=True)
        st.toggle("Agent status changes", value=True)
        st.toggle("Performance threshold alerts", value=False)

        sp(".5rem")
        if st.button("💾 Save Notification Preferences", type="primary"):
            st.success("✅ Notification preferences saved!")

    # ── Security tab ─────────────────────────────────────────────
    with tab4:
        sp(".5rem")
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🔑 Change Password</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            cur_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
        with c2:
            st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)
            conf_pwd = st.text_input("Confirm New Password", type="password")

        if st.button("🔐 Update Password", type="primary"):
            if not all([cur_pwd, new_pwd, conf_pwd]):
                st.warning("⚠️ Please fill in all password fields")
            elif new_pwd != conf_pwd:
                st.warning("⚠️ New passwords don't match")
            elif len(new_pwd) < 8:
                st.warning("⚠️ Password must be at least 8 characters")
            else:
                st.success("✅ Password changed successfully!")

        sp(".75rem")
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">🔐 Two-Factor Authentication</div>', unsafe_allow_html=True)
        tfa_enabled = st.toggle("Enable 2FA", value=False)
        if tfa_enabled:
            st.info("📱 Scan the QR code below with your authenticator app")
            st.code("otpauth://totp/AgentFlow:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=AgentFlow")

        sp(".75rem")
        st.markdown(f'<div style="font-size:.65rem;font-weight:700;color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.6rem;">📋 Active Sessions</div>', unsafe_allow_html=True)
        import pandas as pd
        st.dataframe(pd.DataFrame([
            {"Device":"MacBook Pro","Location":"Ho Chi Minh City, VN","Last Active":"Just now","Status":"🟢 Active"},
            {"Device":"iPhone 15","Location":"Ho Chi Minh City, VN","Last Active":"2 hrs ago","Status":"🟢 Active"},
            {"Device":"Unknown Device","Location":"Unknown","Last Active":"3 days ago","Status":"🔴 Suspicious"},
        ]), use_container_width=True, hide_index=True)

        sp(".5rem")
        if st.button("🔒 Revoke All Other Sessions", type="secondary"):
            st.success("✅ All other sessions revoked")
    
    sp("1.5rem")
