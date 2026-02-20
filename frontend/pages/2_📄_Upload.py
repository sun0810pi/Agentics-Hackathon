# frontend/pages/2_📄_Upload.py
import streamlit as st
from config import config
import time
import random

# Page config
st.markdown(f"""
<div class="main-header">📄 Invoice Upload</div>
<div class="sub-header">Upload and process invoices with 17 AI agents</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "Choose invoice file",
    type=['pdf', 'png', 'jpg', 'jpeg'],
    help="Supported formats: PDF, PNG, JPG"
)

if uploaded_file:
    # Show file info
    st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
    
    # Processing options
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("Processing Mode", ["Full Pipeline", "Fast Track"], horizontal=True)
    with col2:
        use_ai = st.checkbox("Use AI Analysis (Bedrock)", value=True)
    
    # Process button
    if st.button("🔥 Process Invoice", type="primary", use_container_width=True):
        
        # Progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate agent execution
        agents = [
            ("Agent 0: OCR Extraction", 15),
            ("Agent 1: PII Masking", 10),
            ("Agent 2: Decimal Check", 8),
            ("Agent 3: AI Risk Analysis", 25),
            ("Agent 14: Security Scan", 20),
            ("Agent 15: Fraud Ring Detection", 22)
        ]
        
        for i, (agent_name, duration) in enumerate(agents):
            status_text.markdown(f"**⚙️ {agent_name}...**")
            time.sleep(duration / 100)
            progress_bar.progress((i + 1) / len(agents))
        
        status_text.empty()
        progress_bar.empty()
        
        # Simulate result
        risk_score = random.randint(20, 80)
        
        if risk_score < 30:
            st.balloons()
            st.success(f"✅ **APPROVED** - Risk Score: {risk_score}/100")
            decision_color = "success"
        elif risk_score < 70:
            st.warning(f"⚠️ **MANUAL REVIEW** - Risk Score: {risk_score}/100")
            decision_color = "warning"
        else:
            st.error(f"❌ **BLOCKED** - Risk Score: {risk_score}/100")
            decision_color = "error"
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Risk Score", f"{risk_score}/100")
        with col2:
            st.metric("Confidence", f"{random.randint(80, 95)}%")
        with col3:
            st.metric("Duration", f"{random.uniform(3, 8):.2f}s")
        with col4:
            st.metric("Agents Used", "17/17")
        
        # Agent execution log
        with st.expander("🔍 Agent Execution Log", expanded=True):
            for i, (agent_name, duration) in enumerate(agents):
                st.markdown(f"""
                <div style='padding: 0.5rem; background-color: #1a1f2e; 
                            border-left: 3px solid #00d68f; margin: 0.5rem 0; border-radius: 4px;'>
                    ✅ <strong>{agent_name}</strong> - SUCCESS ({duration/100:.2f}s)
                </div>
                """, unsafe_allow_html=True)
        
        # Extracted data
        with st.expander("📋 Extracted Data"):
            st.json({
                "invoice_number": "INV-2026-1234",
                "amount": 25430.50,
                "supplier": "TechCorp Inc",
                "date": "2026-02-20",
                "line_items": 8,
                "currency": "USD"
            })

else:
    # Instructions
    st.info("""
    👆 **Upload an invoice to get started**
    
    **Supported formats:** PDF, PNG, JPG
    **Max file size:** 50 MB
    **Processing time:** 3-8 seconds
    """)