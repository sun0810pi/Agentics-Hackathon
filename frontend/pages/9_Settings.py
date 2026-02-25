import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")
from components.sidebar import render_sidebar
try:
    render_sidebar()
except Exception as _e:
    st.sidebar.error(f"Sidebar error: {_e}")
from components.widgets import (
    success_box,
    warning_box,
    card_container,
    alert_box
)
from auth.login import logout
import logging

logger = logging.getLogger(__name__)

# Page header
st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Manage your account and preferences</p>', unsafe_allow_html=True)

# Settings tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Profile",
    "🎨 Appearance",
    "🔔 Notifications",
    "🔐 Security",
    "🌐 Advanced"
])

with tab1:
    st.markdown("### 👤 Profile Settings")
    
    with card_container("User Information", "ℹ️", variant='primary'):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name",
                value=st.session_state.get('user_name', 'Admin User')
            )
            
            email = st.text_input(
                "Email",
                value=st.session_state.get('user_email', 'admin@agentflow.ai'),
                disabled=True,
                help="Email cannot be changed"
            )
        
        with col2:
            role = st.text_input(
                "Role",
                value=(st.session_state.get('user_role') or 'viewer').title(),
                disabled=True,
                help="Role is assigned by administrators"
            )
            
            timezone = st.selectbox(
                "Timezone",
                options=['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo'],
                index=0
            )
        
        language = st.selectbox(
            "Language",
            options=['English', 'Vietnamese', 'Spanish', 'French'],
            index=0
        )
        
        if st.button("💾 Save Profile", type="primary"):
            st.session_state.user_name = name
            success_box("✅ Profile updated successfully!")

with tab2:
    st.markdown("### 🎨 Appearance Settings")
    
    with card_container("Theme", "🌓", variant='primary'):
        current_theme = st.session_state.get('theme', 'dark')
        
        theme_option = st.radio(
            "Select Theme",
            options=['dark', 'light'],
            format_func=lambda x: '🌙 Dark Mode' if x == 'dark' else '☀️ Light Mode',
            index=0 if current_theme == 'dark' else 1,
            horizontal=True
        )
        
        if theme_option != current_theme:
            if st.button("Apply Theme", type="primary"):
                st.session_state.theme = theme_option
                success_box(f"✅ Switched to {theme_option} theme!")
                st.rerun()
    
    with card_container("Display Options", "👁️", variant='default'):
        compact_mode = st.checkbox("Compact Mode", value=False, help="Reduce spacing for more content")
        show_animations = st.checkbox("Enable Animations", value=True)
        show_tooltips = st.checkbox("Show Tooltips", value=True)
        
        if st.button("💾 Save Display Settings"):
            success_box("✅ Display settings saved!")

with tab3:
    st.markdown("### 🔔 Notification Settings")
    
    with card_container("Email Notifications", "📧", variant='info'):
        st.markdown("**Receive email notifications for:**")
        
        email_fraud_alerts = st.checkbox("🚨 Fraud Alerts", value=True)
        email_high_risk = st.checkbox("⚠️ High Risk Invoices", value=True)
        email_system_updates = st.checkbox("🔄 System Updates", value=False)
        email_weekly_report = st.checkbox("📊 Weekly Reports", value=True)
        
        email_frequency = st.selectbox(
            "Email Frequency",
            options=['Immediate', 'Daily Digest', 'Weekly Digest'],
            index=0
        )
    
    with card_container("In-App Notifications", "🔔", variant='info'):
        st.markdown("**Show in-app notifications for:**")
        
        app_fraud_detected = st.checkbox("🚨 Fraud Detected", value=True, key="app_fraud")
        app_processing_complete = st.checkbox("✅ Processing Complete", value=True, key="app_complete")
        app_system_alerts = st.checkbox("⚠️ System Alerts", value=True, key="app_alerts")
    
    if st.button("💾 Save Notification Settings", type="primary"):
        success_box("✅ Notification preferences saved!")

with tab4:
    st.markdown("### 🔐 Security Settings")
    
    with card_container("Change Password", "🔑", variant='warning'):
        st.markdown("Update your password to keep your account secure.")
        
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("🔒 Change Password", type="primary"):
            if not current_password or not new_password or not confirm_password:
                warning_box("⚠️ Please fill in all password fields")
            elif new_password != confirm_password:
                warning_box("⚠️ New passwords don't match")
            elif len(new_password) < 8:
                warning_box("⚠️ Password must be at least 8 characters")
            else:
                success_box("✅ Password changed successfully!")
    
    with card_container("Two-Factor Authentication", "🔐", variant='success'):
        mfa_enabled = st.session_state.get('mfa_enabled', False)
        
        st.markdown(f"**Status:** {'✅ Enabled' if mfa_enabled else '❌ Disabled'}")
        
        if not mfa_enabled:
            st.markdown("""
            Two-factor authentication adds an extra layer of security to your account.
            You'll need your password and a verification code to sign in.
            """)
            
            if st.button("🔐 Enable 2FA", type="primary"):
                st.session_state.mfa_enabled = True
                success_box("✅ 2FA enabled! Scan this QR code with your authenticator app:")
                st.image("https://via.placeholder.com/200x200?text=QR+Code", width=200)
        else:
            st.markdown("Two-factor authentication is currently enabled for your account.")
            
            if st.button("🔓 Disable 2FA"):
                st.session_state.mfa_enabled = False
                warning_box("⚠️ 2FA has been disabled")
    
    with card_container("Active Sessions", "📱", variant='default'):
        st.markdown("**Current Sessions:**")
        
        sessions = [
            {'device': 'Chrome on Windows', 'location': 'Pleiku, VN', 'last_active': 'Now'},
            {'device': 'Safari on iPhone', 'location': 'Pleiku, VN', 'last_active': '2 hours ago'},
        ]
        
        for i, session in enumerate(sessions):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                **{session['device']}**  
                {session['location']} • {session['last_active']}
                """)
            
            with col2:
                if session['last_active'] != 'Now':
                    if st.button("🚫 Revoke", key=f"revoke_{i}"):
                        success_box(f"✅ Session revoked")

with tab5:
    st.markdown("### 🌐 Advanced Settings")
    
    with card_container("Developer Options", "🔧", variant='warning'):
        st.markdown("**API Access:**")
        
        enable_api = st.checkbox("Enable API Access", value=True)
        
        if enable_api:
            st.code("API Endpoint: https://api.agentflow.ai/v1", language="text")
            st.code(f"API Key: agf_{st.session_state.get('user_email', 'user').split('@')[0]}_***", language="text")
            
            if st.button("🔄 Regenerate API Key"):
                success_box("✅ New API key generated!")
    
    with card_container("Data & Privacy", "🔒", variant='info'):
        st.markdown("**Data Management:**")
        
        if st.button("📥 Export My Data"):
            st.info("Data export will be emailed to you within 24 hours")
        
        if st.button("🗑️ Delete My Account", type="secondary"):
            st.error("⚠️ This action cannot be undone!")
            
            confirm = st.checkbox("I understand that deleting my account is permanent")
            
            if confirm:
                if st.button("⚠️ Confirm Deletion"):
                    alert_box("Account deletion requested. You will be logged out.", "error")
    
    with card_container("System Information", "ℹ️", variant='default'):
        st.markdown(f"""
        **Frontend Version:** {st.session_state.get('app_version', '3.1.0')}  
        **Backend Version:** 3.1.0  
        **Last Updated:** 2026-02-24  
        **Build:** production  
        **Region:** ap-southeast-1
        """)

st.divider()

# Danger zone
st.markdown("### ⚠️ Danger Zone")

with card_container("Logout & Reset", "🚪", variant='danger'):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset All Settings", use_container_width=True):
            st.warning("⚠️ All settings will be reset to defaults")