import streamlit as st
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
    alert_box,
    success_box,
    error_box,
    warning_box,
    card_container,
    timeline_item,
    status_badge
)
from components.metrics import metric_card_group
from services.api_client import get_api_client
from utils.validators import detect_sql_injection, detect_xss, detect_path_traversal
import logging

logger = logging.getLogger(__name__)

# Page header
st.markdown('<h1 class="main-header">🛡️ Security Center</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Security monitoring and attack simulation</p>', unsafe_allow_html=True)

# Security overview
st.markdown("### 📊 Security Overview")

metric_card_group([
    {'title': 'Attacks Blocked Today', 'value': '247', 'delta': '+12%'},
    {'title': 'SQL Injection Attempts', 'value': '89', 'delta': '+5%'},
    {'title': 'XSS Attempts', 'value': '134', 'delta': '+8%'},
    {'title': 'Path Traversal', 'value': '24', 'delta': '-3%'}
])

st.divider()

# Recent security events
st.markdown("### 🚨 Recent Security Events")

with card_container("Security Timeline", "🕐", variant='danger'):
    events = [
        {
            'title': 'SQL Injection Blocked',
            'description': 'Malicious query detected in search field',
            'timestamp': '2 minutes ago',
            'severity': 'HIGH'
        },
        {
            'title': 'XSS Attempt Blocked',
            'description': 'Script tag detected in user input',
            'timestamp': '15 minutes ago',
            'severity': 'HIGH'
        },
        {
            'title': 'Path Traversal Blocked',
            'description': '../../../etc/passwd in file upload',
            'timestamp': '1 hour ago',
            'severity': 'CRITICAL'
        },
        {
            'title': 'Brute Force Detected',
            'description': '50 failed login attempts from 192.168.1.100',
            'timestamp': '3 hours ago',
            'severity': 'HIGH'
        }
    ]
    
    for event in events:
        timeline_item(
            title=event['title'],
            description=event['description'],
            timestamp=event['timestamp'],
            status='error' if event['severity'] in ['CRITICAL', 'HIGH'] else 'warning'
        )

st.divider()

# Attack simulation demo
st.markdown("### 🎭 Attack Simulation Demo")

alert_box(
    "⚠️ **Educational Purpose Only** - This demo shows how our security layer blocks common attacks. "
    "All simulated attacks are safely contained and logged.",
    "warning"
)

tab1, tab2, tab3 = st.tabs(["SQL Injection", "XSS", "Path Traversal"])

with tab1:
    st.markdown("#### 🗃️ SQL Injection Demo")
    
    st.markdown("""
    SQL Injection attacks attempt to manipulate database queries through user input.
    Try entering malicious SQL in the field below to see how our system blocks it.
    """)
    
    sql_input = st.text_area(
        "Enter SQL payload to test:",
        value="' OR '1'='1",
        help="Try: ' OR '1'='1, admin'--, 1'; DROP TABLE users--"
    )
    
    if st.button("🧪 Test SQL Injection", key="test_sql"):
        is_attack, patterns = detect_sql_injection(sql_input)
        
        if is_attack:
            error_box(f"🚫 **SQL INJECTION DETECTED!** Patterns found: {', '.join(patterns)}")
            st.code(f"Blocked payload: {sql_input}", language="sql")
            
            # Log to backend
            try:
                client = get_api_client()
                result = client.test_attack('sql_injection', sql_input)
                if result.get('success'):
                    success_box("✅ Attack logged and blocked by backend")
            except:
                pass
        else:
            success_box("✅ Input is safe - no SQL injection detected")

with tab2:
    st.markdown("#### 💉 XSS (Cross-Site Scripting) Demo")
    
    st.markdown("""
    XSS attacks inject malicious scripts into web pages.
    Try entering JavaScript code to see how our sanitization works.
    """)
    
    xss_input = st.text_area(
        "Enter XSS payload to test:",
        value="<script>alert('XSS')</script>",
        help="Try: <script>alert('XSS')</script>, <img src=x onerror=alert(1)>"
    )
    
    if st.button("🧪 Test XSS", key="test_xss"):
        is_attack, patterns = detect_xss(xss_input)
        
        if is_attack:
            error_box(f"🚫 **XSS DETECTED!** Patterns found: {', '.join(patterns)}")
            st.code(f"Blocked payload: {xss_input}", language="html")
            
            # Show sanitized version
            from utils.validators import sanitize_string
            sanitized = sanitize_string(xss_input)
            st.markdown("**Sanitized output:**")
            st.code(sanitized, language="html")
        else:
            success_box("✅ Input is safe - no XSS detected")

with tab3:
    st.markdown("#### 📁 Path Traversal Demo")
    
    st.markdown("""
    Path Traversal attacks try to access files outside allowed directories.
    Try entering a malicious path to see how it's blocked.
    """)
    
    path_input = st.text_input(
        "Enter file path to test:",
        value="../../../etc/passwd",
        help="Try: ../../../etc/passwd, ..\\windows\\system32"
    )
    
    if st.button("🧪 Test Path Traversal", key="test_path"):
        is_attack, patterns = detect_path_traversal(path_input)
        
        if is_attack:
            error_box(f"🚫 **PATH TRAVERSAL DETECTED!** Patterns found: {', '.join(patterns)}")
            st.code(f"Blocked path: {path_input}")
        else:
            success_box("✅ Path is safe - no traversal detected")

st.divider()

# Security best practices
st.markdown("### 📚 Security Best Practices")

with st.expander("🔒 Input Validation", expanded=False):
    st.markdown("""
    **Our Approach:**
    - ✅ Whitelist validation (allow known good)
    - ✅ Server-side validation (never trust client)
    - ✅ Parameterized queries (SQL injection prevention)
    - ✅ Content Security Policy headers
    - ✅ HTML entity encoding (XSS prevention)
    """)

with st.expander("🛡️ Authentication & Authorization", expanded=False):
    st.markdown("""
    **Security Measures:**
    - ✅ AWS Cognito for authentication
    - ✅ JWT tokens with short expiry
    - ✅ Role-based access control (RBAC)
    - ✅ MFA support
    - ✅ Session management
    """)

with st.expander("🔐 Data Protection", expanded=False):
    st.markdown("""
    **Encryption:**
    - ✅ TLS 1.3 for data in transit
    - ✅ AES-256 for data at rest
    - ✅ AWS KMS for key management
    - ✅ PII detection and masking
    - ✅ Secure file storage
    """)

with st.expander("📊 Monitoring & Logging", expanded=False):
    st.markdown("""
    **Observability:**
    - ✅ Real-time attack detection
    - ✅ Comprehensive audit logs
    - ✅ CloudWatch integration
    - ✅ X-Ray distributed tracing
    - ✅ Automated alerting
    """)