import os
import streamlit as st


class Config:
    """Centralized configuration"""

    # ── App metadata ─────────────────────────────────────
    APP_NAME    = "AgentFlow Finance Guard"
    APP_VERSION = "3.1.0"
    APP_ICON    = "🛡️"
    HACKATHON   = "SWIN Hackathon 2026"

    # ── Deployment ────────────────────────────────────────
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local")  # local | hybrid | production

    # ── Risk thresholds (used in helpers.py → get_risk_color) ──
    RISK_THRESHOLD_LOW    = 30   # 0–29  → green
    RISK_THRESHOLD_MEDIUM = 70   # 30–69 → yellow, 70+ → red

    # ── Debug flag ────────────────────────────────────────
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    # ── Backend ───────────────────────────────────────────
    @classmethod
    def get_backend_url(cls) -> str:
        """Get backend URL — secrets.toml first, then env var, then default."""
        try:
            return st.secrets.get("backend", {}).get("url", "http://localhost:8000")
        except Exception:
            return os.getenv("BACKEND_URL", "http://localhost:8000")

    @classmethod
    def get_backend_timeout(cls) -> int:
        """
        Request timeout in seconds for backend API calls.
        Override via BACKEND_TIMEOUT env var.
        """
        return int(os.getenv("BACKEND_TIMEOUT", "60"))

    @classmethod
    def get_demo_mode(cls) -> str:
        """
        Return "demo" or "production".

        Priority:
        1. DEMO_MODE env var   (DEMO_MODE=true → "demo")
        2. secrets.toml        ([app] demo_mode = true)
        3. Default: "demo"     (safe default for local/hackathon)

        Used by:
            data_provider.py → config.get_demo_mode() == "demo"
            login.py         → config.get_demo_mode() == "demo"
        """
        env_val = os.getenv("DEMO_MODE", "").lower()
        if env_val in ("true", "1", "yes"):
            return "demo"
        if env_val in ("false", "0", "no"):
            return "production"
        try:
            demo = st.secrets.get("app", {}).get("demo_mode", True)
            return "demo" if demo else "production"
        except Exception:
            pass
        return "demo"

    @classmethod
    def get_cognito_config(cls) -> dict:
        """
        Return AWS Cognito config dict.

        Keys: user_pool_id, client_id, region

        If not configured, returns empty strings so
        CognitoClient.is_configured == False → falls back to demo auth.

        Override via:
            env vars:     COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID, AWS_REGION
            secrets.toml: [cognito] user_pool_id = "..."
        """
        try:
            cognito_secrets = st.secrets.get("cognito", {})
            if cognito_secrets.get("user_pool_id"):
                return {
                    "user_pool_id": cognito_secrets.get("user_pool_id", ""),
                    "client_id":    cognito_secrets.get("client_id", ""),
                    "region":       cognito_secrets.get("region", "us-east-1"),
                }
        except Exception:
            pass
        return {
            "user_pool_id": os.getenv("COGNITO_USER_POOL_ID", ""),
            "client_id":    os.getenv("COGNITO_CLIENT_ID", ""),
            "region":       os.getenv("AWS_REGION", "us-east-1"),
        }

    # ── Demo users ────────────────────────────────────────
    # Passwords MUST match what login.py shows in Demo Credentials box.
    DEMO_USERS = {
        "admin@agentflow.ai": {
            "password": "Admin@2026!",
            "role":     "admin",
            "name":     "Admin User",
        },
        "analyst@agentflow.ai": {
            "password": "Analyst@2026!",
            "role":     "analyst",
            "name":     "Risk Analyst",
        },
        "viewer@agentflow.ai": {
            "password": "Viewer@2026!",
            "role":     "viewer",
            "name":     "Viewer",
        },
    }

    # ── Agent metadata ────────────────────────────────────
    TOTAL_AGENTS = 17
    AGENT_TIERS = {
        "Core Detection":   [0, 1, 2, 3, 4, 5, 6, 7],
        "ML Intelligence":  [8, 9, 10],
        "Merchant Success": [11, 12, 13],
        "Security":         [14, 15, 16],
    }

    # ── Translations (includes all keys login.py uses) ────
    TRANSLATIONS = {
        "EN": {
            "login":           "Login",
            "signup":          "Sign Up",
            "email":           "Email Address",
            "password":        "Password",
            "remember":        "Remember Me",
            "forgot":          "Forgot Password?",
            "forgot_password": "Forgot Password?",  # alias for login.py
            "overview":        "Overview",
            "upload":          "Upload",
            "fraud":           "Fraud Detection",
            "logout":          "Logout",
        },
        "VI": {
            "login":           "Đăng nhập",
            "signup":          "Đăng ký",
            "email":           "Địa chỉ Email",
            "password":        "Mật khẩu",
            "remember":        "Ghi nhớ",
            "forgot":          "Quên mật khẩu?",
            "forgot_password": "Quên mật khẩu?",    # alias
            "overview":        "Tổng quan",
            "upload":          "Tải lên",
            "fraud":           "Phát hiện gian lận",
            "logout":          "Đăng xuất",
        },
    }


config = Config()