import os
import streamlit as st

class Config:
    """Centralized configuration"""
    
    # App metadata
    APP_NAME = "AgentFlow Finance Guard"
    APP_VERSION = "3.1.0"
    APP_ICON = "🛡️"
    HACKATHON = "SWIN Hackathon 2026"
    
    # Deployment
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local")  # local | hybrid | production
    
    # Backend
    @classmethod
    def get_backend_url(cls):
        """Get backend URL from secrets or env"""
        try:
            return st.secrets.get("backend", {}).get("url", "http://localhost:8000")
        except:
            return os.getenv("BACKEND_URL", "http://localhost:8000")
    
    BACKEND_URL = property(get_backend_url)
    BACKEND_TIMEOUT = 60
    
    # Users (demo)
    DEMO_USERS = {
        "admin@agentflow.ai": {
            "password": "admin123",
            "role": "admin",
            "name": "Admin User"
        },
        "analyst@agentflow.ai": {
            "password": "analyst123",
            "role": "analyst",
            "name": "Risk Analyst"
        },
        "viewer@agentflow.ai": {
            "password": "viewer123",
            "role": "viewer",
            "name": "Viewer"
        }
    }
    
    # Agent info
    TOTAL_AGENTS = 17
    AGENT_TIERS = {
        "Core Detection": [0, 1, 2, 3, 4, 5, 6, 7],
        "ML Intelligence": [8, 9, 10],
        "Merchant Success": [11, 12, 13],
        "Security": [14, 15, 16]
    }
    
    # Translations
    TRANSLATIONS = {
        "EN": {
            "login": "Login",
            "email": "Email Address",
            "password": "Password",
            "remember": "Remember Me",
            "forgot": "Forgot Password?",
            "overview": "Overview",
            "upload": "Upload",
            "fraud": "Fraud Detection",
            "logout": "Logout"
        },
        "VI": {
            "login": "Đăng nhập",
            "email": "Địa chỉ Email",
            "password": "Mật khẩu",
            "remember": "Ghi nhớ",
            "forgot": "Quên mật khẩu?",
            "overview": "Tổng quan",
            "upload": "Tải lên",
            "fraud": "Phát hiện gian lận",
            "logout": "Đăng xuất"
        }
    }

config = Config()