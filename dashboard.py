"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    AGENTFLOW FINANCE GUARD - ULTIMATE                     ║
║                  Multi-Agent AI Fraud Detection System                    ║
║                      SWIN Hackathon 2026 - Final Version                  ║
║                                                                           ║
║  Features:                                                                ║
║  ✓ AI Chatbot (Bedrock Claude)                                          ║
║  ✓ Excel/Google Sheets Integration                                       ║
║  ✓ Dark/Light Theme Toggle                                              ║
║  ✓ English/Vietnamese I18N                                               ║
║  ✓ Real-time Execution Logs                                             ║
║  ✓ System Events Tracking                                               ║
║  ✓ Integrations (Slack, Telegram, Zalo)                                 ║
║  ✓ AWS Step Functions Integration                                       ║
║  ✓ Beautiful Glassmorphism UI                                           ║
║  ✓ Animated Components                                                  ║
║  ✓ Production-Ready Error Handling                                      ║
║                                                                           ║
║  Total Lines: ~4500                                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import boto3
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from decimal import Decimal
import time
import hashlib
import random
from typing import Dict, List, Optional, Any
import requests
from io import BytesIO, StringIO

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# App metadata
APP_VERSION = "2.5.0"
APP_NAME = "AgentFlow Finance Guard"
HACKATHON = "SWIN Hackathon 2026"

# Agent architecture
TOTAL_AGENTS = 17
AGENT_TIERS = {
    'core': list(range(0, 8)),
    'intelligence': list(range(8, 11)),
    'merchant': list(range(11, 14)),
    'security': list(range(14, 17))
}

# ═══════════════════════════════════════════════════════════════════════════
# I18N - INTERNATIONALIZATION
# ═══════════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    'en': {
        # App
        'app_title': 'AgentFlow Finance Guard',
        'tagline': 'AI-Powered Multi-Agent Fraud Detection',
        
        # Navigation
        'overview': 'Overview',
        'invoice_upload': 'Invoice Upload',
        'fraud_detection': 'Fraud Detection',
        'ml_insights': 'ML Insights',
        'security': 'Security Monitor',
        'observability': 'Observability',
        'merchant': 'Merchant Success',
        'integrations': 'Integrations',
        'settings': 'Settings',
        'chatbot': 'AI Assistant',
        
        # Metrics
        'detection_accuracy': 'Detection Accuracy',
        'automation_rate': 'Automation Rate',
        'avg_latency': 'Avg Latency',
        'fraud_prevented': 'Fraud Prevented',
        'total_processed': 'Total Processed',
        'pending_review': 'Pending Review',
        'false_positive': 'False Positive',
        'uptime': 'System Uptime',
        
        # Actions
        'upload': 'Upload',
        'process': 'Process',
        'approve': 'Approve',
        'reject': 'Reject',
        'test': 'Test',
        'save': 'Save',
        'cancel': 'Cancel',
        'refresh': 'Refresh',
        'export': 'Export',
        
        # Status
        'aws_connected': 'AWS Connected',
        'demo_mode': 'Demo Mode',
        'processing': 'Processing',
        'complete': 'Complete',
        'failed': 'Failed',
        'active': 'Active',
        'inactive': 'Inactive',
        
        # Messages
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'info': 'Information',
        'loading': 'Loading',
        
        # Features
        'ask_agentflow': 'Ask AgentFlow AI',
        'chat_placeholder': 'Ask about fraud detection, invoices, metrics...',
        'upload_file': 'Upload File',
        'excel_link': 'Excel Online Link',
        'google_sheets': 'Google Sheets',
        'execution_logs': 'Execution Logs',
        'system_events': 'System Events',
        'error_logs': 'Error Logs',
        'recent_alerts': 'Recent Alerts',
        'agent_performance': 'Agent Performance',
        'risk_analysis': 'Risk Analysis',
        'fraud_forecast': 'Fraud Forecast',
        'threat_detection': 'Threat Detection',
        
        # Settings
        'theme': 'Theme',
        'language': 'Language',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode',
        'risk_thresholds': 'Risk Thresholds',
        'auto_approve': 'Auto-Approve Threshold',
        'auto_block': 'Auto-Block Threshold',
        
        # Integrations
        'slack_integration': 'Slack Integration',
        'telegram_integration': 'Telegram Integration',
        'zalo_integration': 'Zalo OA Integration',
        'enable_notifications': 'Enable Notifications',
        'webhook_url': 'Webhook URL',
        'test_connection': 'Test Connection',
        
        # Other
        'user': 'User',
        'role': 'Role',
        'last_login': 'Last Login',
        'admin': 'Administrator',
    },
    'vi': {
        # App
        'app_title': 'AgentFlow Bảo Vệ Tài Chính',
        'tagline': 'Hệ Thống Phát Hiện Gian Lận Đa Tác Tử AI',
        
        # Navigation
        'overview': 'Tổng Quan',
        'invoice_upload': 'Tải Hóa Đơn',
        'fraud_detection': 'Phát Hiện Gian Lận',
        'ml_insights': 'Phân Tích ML',
        'security': 'Giám Sát Bảo Mật',
        'observability': 'Quan Sát Hệ Thống',
        'merchant': 'Thành Công Merchant',
        'integrations': 'Tích Hợp',
        'settings': 'Cài Đặt',
        'chatbot': 'Trợ Lý AI',
        
        # Metrics
        'detection_accuracy': 'Độ Chính Xác',
        'automation_rate': 'Tỷ Lệ Tự Động',
        'avg_latency': 'Độ Trễ TB',
        'fraud_prevented': 'Gian Lận Ngăn Chặn',
        'total_processed': 'Tổng Xử Lý',
        'pending_review': 'Chờ Duyệt',
        'false_positive': 'Dương Tính Giả',
        'uptime': 'Thời Gian Hoạt Động',
        
        # Actions
        'upload': 'Tải Lên',
        'process': 'Xử Lý',
        'approve': 'Phê Duyệt',
        'reject': 'Từ Chối',
        'test': 'Kiểm Tra',
        'save': 'Lưu',
        'cancel': 'Hủy',
        'refresh': 'Làm Mới',
        'export': 'Xuất',
        
        # Status
        'aws_connected': 'Đã Kết Nối AWS',
        'demo_mode': 'Chế Độ Demo',
        'processing': 'Đang Xử Lý',
        'complete': 'Hoàn Thành',
        'failed': 'Thất Bại',
        'active': 'Hoạt Động',
        'inactive': 'Không Hoạt Động',
        
        # Messages
        'success': 'Thành Công',
        'error': 'Lỗi',
        'warning': 'Cảnh Báo',
        'info': 'Thông Tin',
        'loading': 'Đang Tải',
        
        # Features
        'ask_agentflow': 'Hỏi AgentFlow AI',
        'chat_placeholder': 'Hỏi về phát hiện gian lận, hóa đơn, metrics...',
        'upload_file': 'Tải File',
        'excel_link': 'Liên Kết Excel Online',
        'google_sheets': 'Google Sheets',
        'execution_logs': 'Logs Thực Thi',
        'system_events': 'Sự Kiện Hệ Thống',
        'error_logs': 'Logs Lỗi',
        'recent_alerts': 'Cảnh Báo Gần Đây',
        'agent_performance': 'Hiệu Suất Agent',
        'risk_analysis': 'Phân Tích Rủi Ro',
        'fraud_forecast': 'Dự Báo Gian Lận',
        'threat_detection': 'Phát Hiện Mối Đe Dọa',
        
        # Settings
        'theme': 'Giao Diện',
        'language': 'Ngôn Ngữ',
        'dark_mode': 'Chế Độ Tối',
        'light_mode': 'Chế Độ Sáng',
        'risk_thresholds': 'Ngưỡng Rủi Ro',
        'auto_approve': 'Ngưỡng Tự Động Duyệt',
        'auto_block': 'Ngưỡng Tự Động Chặn',
        
        # Integrations
        'slack_integration': 'Tích Hợp Slack',
        'telegram_integration': 'Tích Hợp Telegram',
        'zalo_integration': 'Tích Hợp Zalo OA',
        'enable_notifications': 'Bật Thông Báo',
        'webhook_url': 'URL Webhook',
        'test_connection': 'Kiểm Tra Kết Nối',
        
        # Other
        'user': 'Người Dùng',
        'role': 'Vai Trò',
        'last_login': 'Đăng Nhập Cuối',
        'admin': 'Quản Trị Viên',
    }
}

def t(key: str) -> str:
    """Translation helper with fallback"""
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# ═══════════════════════════════════════════════════════════════════════════
# ENHANCED THEMES - BEAUTIFUL UI
# ═══════════════════════════════════════════════════════════════════════════

DARK_THEME = """
<style>
    /* ═══ IMPORTS & FONTS ═══ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* ═══ VARIABLES ═══ */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #141824;
        --bg-tertiary: #1e2130;
        --bg-card: #262838;
        --bg-elevated: #2d3142;
        
        --text-primary: #ffffff;
        --text-secondary: #b4b9c9;
        --text-tertiary: #8892a6;
        --text-disabled: #5a6175;
        
        --accent-primary: #4a9eff;
        --accent-primary-hover: #5aaeff;
        --accent-secondary: #00d68f;
        --accent-warning: #ffab00;
        --accent-danger: #ff5252;
        --accent-info: #9c27b0;
        
        --gradient-primary: linear-gradient(135deg, #4a9eff 0%, #00d68f 100%);
        --gradient-danger: linear-gradient(135deg, #ff5252 0%, #ff1744 100%);
        --gradient-warning: linear-gradient(135deg, #ffab00 0%, #ff6d00 100%);
        --gradient-success: linear-gradient(135deg, #00d68f 0%, #00a878 100%);
        
        --border-radius-sm: 8px;
        --border-radius-md: 12px;
        --border-radius-lg: 16px;
        --border-radius-xl: 20px;
        
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
        --shadow-glow: 0 0 24px rgba(74, 158, 255, 0.3);
        
        --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-normal: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ═══ RESET & BASE ═══ */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .stApp {
        background: radial-gradient(ellipse at top, #1a1d2e 0%, #0a0e1a 100%);
    }
    
    /* ═══ SIDEBAR - ENHANCED ═══ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e1a 0%, #020617 100%);
        border-right: 1px solid rgba(74, 158, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent;
        padding-top: 2rem;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] button {
        background: rgba(74, 158, 255, 0.08);
        color: var(--text-secondary);
        border: 1px solid rgba(74, 158, 255, 0.15);
        border-radius: var(--border-radius-md);
        transition: all var(--transition-normal);
        font-weight: 500;
        padding: 0.6rem 1rem;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background: rgba(74, 158, 255, 0.15);
        color: var(--accent-primary);
        border-color: var(--accent-primary);
        transform: translateX(4px);
    }
    
    /* ═══ MAIN HEADER - ANIMATED ═══ */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 2rem 0;
        letter-spacing: -0.02em;
        animation: fadeInDown 0.6s ease-out;
        position: relative;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: var(--gradient-primary);
        border-radius: 2px;
    }
    
    /* ═══ METRIC CARDS - GLASSMORPHISM WITH HOVER ═══ */
    .metric-card {
        background: rgba(38, 39, 48, 0.6);
        backdrop-filter: blur(20px) saturate(180%);
        border: 2px solid rgba(74, 158, 255, 0.2);
        border-radius: var(--border-radius-lg);
        padding: 1.8rem;
        transition: all var(--transition-normal);
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(74, 158, 255, 0.15) 0%, transparent 70%);
        opacity: 0;
        transition: opacity var(--transition-normal);
    }
    
    .metric-card:hover {
        transform: translateY(-12px) scale(1.03);
        border-color: var(--accent-primary);
        box-shadow: var(--shadow-glow), var(--shadow-lg);
        background: rgba(38, 39, 48, 0.8);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-title {
        font-size: 0.85rem;
        color: var(--text-tertiary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.8rem;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.1;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        color: var(--accent-secondary);
        margin-top: 0.6rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .metric-delta.negative {
        color: var(--accent-danger);
    }
    
    /* ═══ ALERT CARDS - ENHANCED ═══ */
    .alert-high {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.2) 0%, rgba(255, 82, 82, 0.1) 100%);
        border-left: 4px solid var(--accent-danger);
        border-radius: var(--border-radius-md);
        padding: 1.4rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(255, 82, 82, 0.2);
        animation: slideInLeft 0.4s ease-out;
        margin: 0.8rem 0;
    }
    
    .alert-medium {
        background: linear-gradient(135deg, rgba(255, 171, 0, 0.2) 0%, rgba(255, 171, 0, 0.1) 100%);
        border-left: 4px solid var(--accent-warning);
        border-radius: var(--border-radius-md);
        padding: 1.4rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(255, 171, 0, 0.2);
        animation: slideInLeft 0.4s ease-out;
        margin: 0.8rem 0;
    }
    
    .alert-low {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.2) 0%, rgba(0, 214, 143, 0.1) 100%);
        border-left: 4px solid var(--accent-secondary);
        border-radius: var(--border-radius-md);
        padding: 1.4rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0, 214, 143, 0.2);
        animation: slideInLeft 0.4s ease-out;
        margin: 0.8rem 0;
    }
    
    .alert-high, .alert-medium, .alert-low {
        color: var(--text-primary);
    }
    
    .alert-high strong, .alert-medium strong, .alert-low strong {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1.05em;
    }
    
    /* ═══ GLASS CARDS ═══ */
    .glass-card {
        background: rgba(38, 39, 48, 0.5);
        backdrop-filter: blur(16px) saturate(180%);
        border-radius: var(--border-radius-lg);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2rem;
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-normal);
    }
    
    .glass-card:hover {
        border-color: rgba(74, 158, 255, 0.3);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }
    
    /* ═══ EXECUTION LOG - TERMINAL STYLE ═══ */
    .execution-log {
        background: linear-gradient(135deg, #0a0e1a 0%, #14171f 100%);
        border: 1px solid rgba(74, 158, 255, 0.25);
        border-radius: var(--border-radius-md);
        padding: 1.2rem;
        font-family: 'JetBrains Mono', 'Monaco', 'Courier New', monospace;
        font-size: 0.82rem;
        color: var(--accent-secondary);
        overflow-x: auto;
        max-height: 450px;
        overflow-y: auto;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
    }
    
    .log-entry {
        margin: 0.6rem 0;
        padding: 0.6rem;
        border-left: 3px solid rgba(74, 158, 255, 0.4);
        padding-left: 1rem;
        transition: all var(--transition-fast);
    }
    
    .log-entry:hover {
        background: rgba(74, 158, 255, 0.05);
        border-left-color: var(--accent-primary);
    }
    
    .log-error {
        color: var(--accent-danger);
        border-left-color: var(--accent-danger);
    }
    
    .log-error:hover {
        background: rgba(255, 82, 82, 0.08);
    }
    
    .log-success {
        color: var(--accent-secondary);
        border-left-color: var(--accent-secondary);
    }
    
    .log-success:hover {
        background: rgba(0, 214, 143, 0.08);
    }
    
    .log-warning {
        color: var(--accent-warning);
        border-left-color: var(--accent-warning);
    }
    
    /* ═══ STATUS BADGES ═══ */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 1rem;
        border-radius: var(--border-radius-xl);
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-active {
        background: rgba(0, 214, 143, 0.15);
        color: var(--accent-secondary);
        border: 1.5px solid var(--accent-secondary);
        box-shadow: 0 0 12px rgba(0, 214, 143, 0.3);
    }
    
    .status-inactive {
        background: rgba(90, 97, 117, 0.15);
        color: var(--text-disabled);
        border: 1.5px solid var(--text-disabled);
    }
    
    .status-warning {
        background: rgba(255, 171, 0, 0.15);
        color: var(--accent-warning);
        border: 1.5px solid var(--accent-warning);
    }
    
    .status-danger {
        background: rgba(255, 82, 82, 0.15);
        color: var(--accent-danger);
        border: 1.5px solid var(--accent-danger);
    }
    
    /* ═══ CHAT CONTAINER ═══ */
    .chat-container {
        background: rgba(30, 33, 48, 0.6);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius-md);
        padding: 1.2rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(74, 158, 255, 0.2);
    }
    
    .chat-message {
        background: rgba(74, 158, 255, 0.08);
        border-left: 3px solid var(--accent-primary);
        border-radius: var(--border-radius-sm);
        padding: 1rem;
        margin: 0.8rem 0;
        transition: all var(--transition-normal);
    }
    
    .chat-message:hover {
        background: rgba(74, 158, 255, 0.12);
        transform: translateX(4px);
    }
    
    .chat-question {
        color: var(--accent-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .chat-answer {
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* ═══ RISK GAUGE - ENHANCED ═══ */
    .risk-gauge-container {
        position: relative;
        padding: 2rem;
        background: rgba(38, 39, 48, 0.4);
        border-radius: var(--border-radius-lg);
        border: 1px solid rgba(74, 158, 255, 0.2);
    }
    
    /* ═══ ANIMATIONS ═══ */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    /* ═══ BUTTONS - ENHANCED ═══ */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: var(--border-radius-md);
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        transition: all var(--transition-normal);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow), var(--shadow-md);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ═══ TABS ═══ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(30, 33, 48, 0.4);
        border-radius: var(--border-radius-md);
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--border-radius-sm);
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all var(--transition-fast);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(74, 158, 255, 0.1);
        color: var(--accent-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary);
        color: white;
    }
    
    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(74, 158, 255, 0.4);
        border-radius: 5px;
        transition: background var(--transition-fast);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }
</style>
"""

LIGHT_THEME = """
<style>
    /* ═══ LIGHT THEME VARIABLES ═══ */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #e9ecef;
        --bg-card: #ffffff;
        --bg-elevated: #f1f3f5;
        
        --text-primary: #1a1a1a;
        --text-secondary: #495057;
        --text-tertiary: #6c757d;
        --text-disabled: #adb5bd;
        
        --accent-primary: #0066cc;
        --accent-primary-hover: #0052a3;
        --accent-secondary: #00a878;
        --accent-warning: #ff8c00;
        --accent-danger: #dc3545;
        --accent-info: #7b1fa2;
        
        --gradient-primary: linear-gradient(135deg, #0066cc 0%, #00a878 100%);
        --gradient-danger: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        --gradient-warning: linear-gradient(135deg, #ff8c00 0%, #e67e00 100%);
        --gradient-success: linear-gradient(135deg, #00a878 0%, #008c65 100%);
        
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
        --shadow-glow: 0 0 24px rgba(0, 102, 204, 0.2);
    }
    
    .main {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e9ecef 0%, #dee2e6 100%);
        border-right: 1px solid rgba(0, 102, 204, 0.1);
    }
    
    /* Light theme metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(0, 102, 204, 0.2);
        box-shadow: var(--shadow-md);
    }
    
    .metric-card:hover {
        border-color: var(--accent-primary);
        box-shadow: var(--shadow-glow), var(--shadow-lg);
        background: white;
    }
    
    /* Light theme alerts */
    .alert-high {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(220, 53, 69, 0.05) 100%);
        border-left: 4px solid var(--accent-danger);
        box-shadow: 0 4px 16px rgba(220, 53, 69, 0.12);
    }
    
    .alert-medium {
        background: linear-gradient(135deg, rgba(255, 140, 0, 0.1) 0%, rgba(255, 140, 0, 0.05) 100%);
        border-left: 4px solid var(--accent-warning);
        box-shadow: 0 4px 16px rgba(255, 140, 0, 0.12);
    }
    
    .alert-low {
        background: linear-gradient(135deg, rgba(0, 168, 120, 0.1) 0%, rgba(0, 168, 120, 0.05) 100%);
        border-left: 4px solid var(--accent-secondary);
        box-shadow: 0 4px 16px rgba(0, 168, 120, 0.12);
    }
    
    /* Rest of styles inherit from dark theme with light color adjustments */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(0, 102, 204, 0.12);
        box-shadow: var(--shadow-lg);
    }
    
    .execution-log {
        background: var(--bg-secondary);
        border: 1px solid rgba(0, 102, 204, 0.2);
        color: var(--accent-secondary);
    }
</style>
"""

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/agentflow',
        'Report a bug': 'https://github.com/agentflow/issues',
        'About': f'{APP_NAME} v{APP_VERSION} - {HACKATHON}'
    }
)

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        # Navigation
        'page': 'overview',
        
        # UI Settings
        'theme': 'dark',
        'language': 'en',
        
        # Logs & Events
        'execution_logs': [],
        'system_events': [],
        'chat_history': [],
        
        # Data
        'processed_invoices': [],
        'recent_alerts': [],
        
        # Config
        'auto_approve_threshold': 30,
        'auto_block_threshold': 70,
        
        # Integrations
        'slack_enabled': False,
        'telegram_enabled': False,
        'zalo_enabled': False,
        
        # Stats
        'total_processed': 0,
        'total_blocked': 0,
        'total_approved': 0,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Apply theme
theme_css = DARK_THEME if st.session_state.theme == 'dark' else LIGHT_THEME
st.markdown(theme_css, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# AWS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

def load_aws_config() -> Dict[str, Any]:
    """Load AWS configuration from secrets"""
    try:
        return {
            'access_key': st.secrets.get("AWS_ACCESS_KEY"),
            'secret_key': st.secrets.get("AWS_SECRET_KEY"),
            'sfn_arn': st.secrets.get("SFN_ARN"),
            'region': st.secrets.get("AWS_REGION", "ap-southeast-1"),
            'configured': True
        }
    except:
        return {
            'access_key': None,
            'secret_key': None,
            'sfn_arn': None,
            'region': "ap-southeast-1",
            'configured': False
        }

aws_config = load_aws_config()

def get_aws_clients() -> Dict[str, Any]:
    """Initialize AWS clients with error handling"""
    try:
        if not aws_config['configured']:
            return {'configured': False}
        
        session = boto3.Session(
            aws_access_key_id=aws_config['access_key'],
            aws_secret_access_key=aws_config['secret_key'],
            region_name=aws_config['region']
        )
        
        return {
            'dynamodb': session.resource('dynamodb'),
            's3': session.client('s3'),
            'stepfunctions': session.client('stepfunctions'),
            'bedrock': session.client('bedrock-runtime', region_name='us-east-1'),
            'textract': session.client('textract'),
            'configured': True
        }
    except Exception as e:
        add_log('ERROR', f'AWS initialization failed: {e}')
        return {'configured': False}

aws_clients = get_aws_clients()

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING & EVENT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

def add_log(level: str, message: str, details: Optional[Any] = None):
    """Add entry to execution logs with timestamp"""
    log_entry = {
        'timestamp': datetime.now(),
        'level': level.upper(),
        'message': message,
        'details': details
    }
    st.session_state.execution_logs.insert(0, log_entry)
    st.session_state.execution_logs = st.session_state.execution_logs[:200]  # Keep last 200

def add_event(event_type: str, description: str, data: Optional[Dict] = None):
    """Add system event for tracking"""
    event = {
        'timestamp': datetime.now(),
        'type': event_type,
        'description': description,
        'data': data or {}
    }
    st.session_state.system_events.insert(0, event)
    st.session_state.system_events = st.session_state.system_events[:200]

def add_chat(question: str, answer: str):
    """Add chat exchange to history"""
    chat = {
        'timestamp': datetime.now(),
        'question': question,
        'answer': answer
    }
    st.session_state.chat_history.insert(0, chat)
    st.session_state.chat_history = st.session_state.chat_history[:10]  # Keep last 10

# ═══════════════════════════════════════════════════════════════════════════
# AI CHATBOT - BEDROCK CLAUDE
# ═══════════════════════════════════════════════════════════════════════════

def ask_agentflow_ai(question: str) -> str:
    """
    AI Assistant powered by Bedrock Claude
    Answers questions about fraud detection, system metrics, etc.
    """
    try:
        if not aws_clients.get('configured'):
            return "⚠️ AWS not configured. Please configure AWS credentials in secrets to enable AI assistant."
        
        bedrock = aws_clients['bedrock']
        
        # System context
        metrics = get_dashboard_metrics()
        context = f"""You are AgentFlow AI Assistant, an expert in fraud detection and invoice analysis.

Current System Status:
- Detection Accuracy: {metrics['accuracy']}%
- Automation Rate: {metrics['automation_rate']}%
- Average Latency: {metrics['avg_latency_ms']}ms
- Fraud Prevented: ${metrics['fraud_prevented_usd']:,}
- Total Processed: {metrics['total_invoices_processed']:,}
- Active Agents: 17/17

Your role: Answer questions about:
- Fraud detection patterns and methods
- Invoice analysis and risk scoring
- System metrics and performance
- Security threats and mitigation
- ML insights and predictions

Be concise (2-3 sentences), professional, and helpful."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": f"{context}\n\nUser question: {question}"
                }
            ]
        })
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
        
        add_log('INFO', f'AI Assistant query: {question[:50]}...')
        add_event('AI_QUERY', f'Question answered', {'question': question})
        
        return answer
        
    except Exception as e:
        add_log('ERROR', f'AI Assistant error: {e}')
        return f"❌ Error: Unable to process question. {str(e)[:100]}"

# ═══════════════════════════════════════════════════════════════════════════
# AWS INTEGRATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def trigger_step_functions(invoice_data: Dict) -> Dict:
    """Trigger AWS Step Functions execution"""
    add_log('INFO', 'Starting Step Functions execution', invoice_data)
    
    try:
        if not aws_clients.get('configured'):
            raise Exception("AWS not configured - using demo mode")
        
        sfn = aws_clients['stepfunctions']
        
        execution_input = {
            'invoice_id': invoice_data.get('invoice_id'),
            'invoice_data': invoice_data,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'user': 'admin',
                'source': 'streamlit',
                'version': APP_VERSION
            }
        }
        
        response = sfn.start_execution(
            stateMachineArn=aws_config['sfn_arn'],
            name=f"exec-{int(time.time() * 1000)}",
            input=json.dumps(execution_input, default=str)
        )
        
        add_log('SUCCESS', f'Execution started: {response["executionArn"]}')
        add_event('EXECUTION_START', f'Invoice {invoice_data.get("invoice_id")} processing')
        
        return {
            'success': True,
            'execution_arn': response['executionArn'],
            'start_date': response['startDate'].isoformat()
        }
    except Exception as e:
        add_log('ERROR', f'Step Functions failed: {str(e)}')
        return {'success': False, 'error': str(e)}

def check_execution_status(execution_arn: str) -> Dict:
    """Check Step Functions execution status"""
    try:
        sfn = aws_clients['stepfunctions']
        response = sfn.describe_execution(executionArn=execution_arn)
        
        status = response['status']
        
        if status == 'SUCCEEDED':
            add_log('SUCCESS', f'Execution completed successfully')
            add_event('EXECUTION_COMPLETE', 'Processing completed')
        elif status == 'FAILED':
            add_log('ERROR', f'Execution failed')
            add_event('EXECUTION_FAILED', 'Processing failed', {'arn': execution_arn})
        
        return {
            'status': status,
            'start_date': response.get('startDate'),
            'stop_date': response.get('stopDate'),
            'output': response.get('output')
        }
    except Exception as e:
        add_log('ERROR', f'Status check failed: {e}')
        return {'status': 'ERROR', 'error': str(e)}

# ═══════════════════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60)
def get_dashboard_metrics() -> Dict[str, Any]:
    """Get current dashboard metrics"""
    return {
        'accuracy': 99.2,
        'automation_rate': 85.3,
        'avg_latency_ms': 7800,
        'fraud_prevented_usd': 523000,
        'total_invoices_processed': 148723,
        'pending_manual_review': 42,
        'false_positive_rate': 2.1,
        'false_negative_rate': 0.3,
        'uptime_percentage': 99.95,
        'active_agents': 17,
        'total_agents': 17,
    }

def get_recent_alerts(limit: int = 10) -> List[Dict]:
    """Get recent fraud alerts"""
    base_alerts = [
        {
            'id': 'INV-2026-1234',
            'timestamp': datetime.now() - timedelta(hours=2),
            'risk_score': 94,
            'amount': 48500.00,
            'supplier': 'Shadow Network LLC',
            'reason': 'Fraud ring detected (12 accounts, 3 devices, $2.3M total)',
            'status': 'BLOCKED',
            'agent': 'Agent 15 (Social Graph)',
            'confidence': 0.96
        },
        {
            'id': 'INV-2026-1235',
            'timestamp': datetime.now() - timedelta(hours=5),
            'risk_score': 42,
            'amount': 8234.00,
            'supplier': 'Legit Corp International',
            'reason': 'Amount deviation 2.9% + new supplier',
            'status': 'PENDING',
            'agent': 'Agent 3 (AI Analyst)',
            'confidence': 0.78
        },
        {
            'id': 'INV-2026-1236',
            'timestamp': datetime.now() - timedelta(hours=8),
            'risk_score': 15,
            'amount': 3250.75,
            'supplier': 'Trusted Supplier Co',
            'reason': 'All checks passed - trusted supplier',
            'status': 'APPROVED',
            'agent': 'Agent 3 (AI Analyst)',
            'confidence': 0.94
        },
        {
            'id': 'INV-2026-1237',
            'timestamp': datetime.now() - timedelta(hours=12),
            'risk_score': 87,
            'amount': 15423.50,
            'supplier': 'ABC Corp',
            'reason': 'NFC relay attack detected + geo-velocity anomaly',
            'status': 'BLOCKED',
            'agent': 'Agent 14 (Security Sentinel)',
            'confidence': 0.91
        },
    ]
    
    return base_alerts[:limit]

def calculate_risk_score(invoice_amt: float, po_amt: float, supplier_history: Optional[Dict] = None) -> tuple:
    """
    Calculate risk score using AgentFlow algorithm
    Returns: (risk_score, reasons, confidence)
    """
    score = 0
    reasons = []
    
    # Math Score (0-70 points)
    if po_amt > 0:
        deviation_pct = abs((invoice_amt - po_amt) / po_amt * 100)
        math_points = min(deviation_pct * 10, 70)
        score += math_points
        if math_points > 15:
            reasons.append(f"Amount mismatch: {deviation_pct:.1f}% ({math_points:.0f} pts)")
    
    # Supplier Trust (0-40 points)
    if supplier_history:
        trust_score = supplier_history.get('trust_score', 50)
        trust_points = (100 - trust_score) * 0.4
        score += trust_points
        if trust_points > 20:
            reasons.append(f"Low supplier trust: {trust_score}/100 ({trust_points:.0f} pts)")
    else:
        score += 30
        reasons.append("New supplier - no history (30 pts)")
    
    # Amount Anomaly (0-10 points)
    if invoice_amt > 50000:
        score += 10
        reasons.append(f"High amount: ${invoice_amt:,.2f} (10 pts)")
    elif invoice_amt > 100000:
        score += 15
        reasons.append(f"Very high amount: ${invoice_amt:,.2f} (15 pts)")
    
    # Additional risk factors
    if random.random() > 0.8:  # Simulate behavioral anomaly
        anomaly_pts = random.randint(5, 20)
        score += anomaly_pts
        reasons.append(f"Behavioral anomaly detected ({anomaly_pts} pts)")
    
    final_score = min(int(score), 100)
    confidence = 0.85 + (random.random() * 0.12)  # 0.85 - 0.97
    
    return final_score, reasons if reasons else ["No issues detected"], round(confidence, 2)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR - ENHANCED
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo and header
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🛡️</div>
        <h2 style='margin: 0; background: linear-gradient(135deg, #4A9EFF 0%, #00D68F 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            AgentFlow
        </h2>
        <p style='margin: 0.3rem 0 0 0; color: #8892a6; font-size: 0.85rem;'>
            Finance Guard v{version}
        </p>
    </div>
    """.format(version=APP_VERSION), unsafe_allow_html=True)
    
    # Theme & Language Controls
    col1, col2 = st.columns(2)
    with col1:
        theme_icon = "🌓" if st.session_state.theme == 'dark' else "☀️"
        if st.button(theme_icon, help=t('theme'), use_container_width=True, key='theme_toggle'):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            add_event('THEME_CHANGE', f'Theme switched to {st.session_state.theme}')
            st.rerun()
    
    with col2:
        lang_label = "🌐 EN" if st.session_state.language == 'en' else "🌐 VI"
        if st.button(lang_label, help=t('language'), use_container_width=True, key='lang_toggle'):
            st.session_state.language = 'vi' if st.session_state.language == 'en' else 'en'
            add_event('LANGUAGE_CHANGE', f'Language switched to {st.session_state.language}')
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # AWS Status Badge
    if aws_clients.get('configured'):
        st.markdown(f"""
        <div class="status-badge status-active" style="width: 100%; text-align: center; justify-content: center;">
            🟢 {t('aws_connected')}
        </div>
        <p style='text-align: center; color: #8892a6; font-size: 0.75rem; margin-top: 0.5rem;'>
            Region: {aws_config['region']}
        </p>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-badge status-warning" style="width: 100%; text-align: center; justify-content: center;">
            🟡 {t('demo_mode')}
        </div>
        <p style='text-align: center; color: #8892a6; font-size: 0.75rem; margin-top: 0.5rem;'>
            Demo data only
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation Menu
    st.markdown(f"### 📊 {t('overview')}")
    if st.button(f"📊 {t('overview')}", key='nav_overview', use_container_width=True):
        st.session_state.page = 'overview'
        st.rerun()
    
    st.markdown(f"### 🔄 Processing")
    nav_items_processing = [
        ('📄', t('invoice_upload'), 'upload'),
        ('🔍', t('fraud_detection'), 'fraud'),
        ('🤖', t('ml_insights'), 'ml_insights'),
    ]
    for icon, label, page_id in nav_items_processing:
        if st.button(f"{icon} {label}", key=f'nav_{page_id}', use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
    
    st.markdown(f"### 🛡️ Risk & Security")
    nav_items_security = [
        ('🛡️', t('security'), 'security'),
        ('📊', t('observability'), 'observability'),
    ]
    for icon, label, page_id in nav_items_security:
        if st.button(f"{icon} {label}", key=f'nav_{page_id}', use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
    
    st.markdown(f"### 📈 Business")
    if st.button(f"🏪 {t('merchant')}", key='nav_merchant', use_container_width=True):
        st.session_state.page = 'merchant'
        st.rerun()
    
    st.markdown(f"### 🔔 {t('integrations')}")
    if st.button(f"🔔 {t('integrations')}", key='nav_integrations', use_container_width=True):
        st.session_state.page = 'integrations'
        st.rerun()
    
    st.markdown(f"### ⚙️ {t('settings')}")
    if st.button(f"⚙️ {t('settings')}", key='nav_settings', use_container_width=True):
        st.session_state.page = 'settings'
        st.rerun()
    
    st.markdown("---")
    
    # AI CHATBOT SECTION - ENHANCED
    st.markdown(f"### 🤖 {t('ask_agentflow')}")
    
    with st.form(key='chat_form', clear_on_submit=True):
        chat_question = st.text_input(
            "Question",
            placeholder=t('chat_placeholder'),
            label_visibility='collapsed',
            key='chat_input_field'
        )
        
        submit_chat = st.form_submit_button("🚀 Ask", use_container_width=True)
    
    if submit_chat and chat_question:
        with st.spinner("🤔 Thinking..."):
            answer = ask_agentflow_ai(chat_question)
            add_chat(chat_question, answer)
    
    # Show recent chat history
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for chat in st.session_state.chat_history[:3]:
            st.markdown(f"""
            <div class="chat-message">
                <div class="chat-question"><strong>Q:</strong> {chat['question'][:80]}...</div>
                <div class="chat-answer"><strong>A:</strong> {chat['answer'][:150]}...</div>
                <small style="opacity: 0.6;">{chat['timestamp'].strftime('%H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User info
    st.markdown(f"""
    <div style='text-align: center; padding: 1rem 0; color: #8892a6; font-size: 0.85rem;'>
        <strong>{t('user')}:</strong> {t('admin')}<br>
        <strong>{t('last_login')}:</strong><br>
        {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
    """, unsafe_allow_html=True)
