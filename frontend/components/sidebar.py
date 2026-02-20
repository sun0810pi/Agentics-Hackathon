# frontend/components/sidebar.py
import streamlit as st
from config import config
from auth.login import logout_user

def render_sidebar():
    """Render sidebar with navigation"""
    
    with st.sidebar:
        # Logo & Title
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <div style='font-size: 3rem;'>{config.APP_ICON}</div>
            <div style='font-size: 1.25rem; font-weight: 700; color: #4A9EFF;'>
                {config.APP_NAME}
            </div>
            <div style='font-size: 0.875rem; color: #a0aec0; margin-top: 0.25rem;'>
                v{config.APP_VERSION}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        user_role = st.session_state.get('user_role', 'guest')
        user_name = st.session_state.get('user_name', 'Guest')
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1a1f2e 0%, #141824 100%); 
                    border: 1px solid rgba(74, 158, 255, 0.3); 
                    border-radius: 8px; 
                    padding: 1rem; 
                    margin-bottom: 1rem;'>
            <div style='font-size: 1rem; font-weight: 600; color: #ffffff;'>👤 {user_name}</div>
            <div style='font-size: 0.875rem; color: #a0aec0; text-transform: capitalize;'>{user_role}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Dark", use_container_width=True, disabled=st.session_state.theme=='dark'):
                st.session_state.theme = 'dark'
                st.rerun()
        with col2:
            if st.button("☀️ Light", use_container_width=True, disabled=st.session_state.theme=='light'):
                st.session_state.theme = 'light'
                st.rerun()
        
        st.markdown("---")
        
        # Stats
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Agents", "17/17", "✅")
        with col2:
            st.metric("Uptime", "99.9%", "+0.1%")
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()