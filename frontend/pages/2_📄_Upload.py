import streamlit as st
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.warning('⚠️ Vui lòng đăng nhập để tiếp tục.')
    st.stop()
from components.sidebar import render_sidebar
render_sidebar()
from components.widgets import alert_box, success_box, error_box, warning_box
from services.data_provider import process_invoice
from utils.validators import validate_file_upload
from utils.helpers import sanitize_filename
import time

st.markdown('<h1 class="main-header">📄 Upload Invoice</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload and analyze invoices</p>', unsafe_allow_html=True)

# Upload section
st.markdown("### 📤 Upload File")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Select invoice (PDF, PNG, JPG)",
        type=['pdf', 'png', 'jpg', 'jpeg']
    )

with col2:
    mode = st.selectbox(
        "Mode",
        ['full', 'fast', 'demo'],
        format_func=lambda x: {
            'full': '🔍 Full (17 agents)',
            'fast': '⚡ Fast (5 agents)',
            'demo': '🎭 Demo'
        }[x]
    )
    
    threshold = st.slider("Auto-approve threshold", 0, 100, 30)

if uploaded_file:
    st.info(f"📋 {uploaded_file.name} ({len(uploaded_file.getvalue())/1024:.1f} KB)")
    
    # Validate
    is_valid, error_msg = validate_file_upload(
        uploaded_file.name,
        uploaded_file.getvalue(),
        50
    )
    
    if not is_valid:
        error_box(f"❌ {error_msg}")
    else:
        if st.button("🚀 Process Invoice", type="primary", use_container_width=True):
            with st.status("Processing...", expanded=True) as status:
                st.write("⬆️ Uploading...")
                time.sleep(0.5)
                
                st.write("🤖 Running analysis...")
                result = process_invoice(
                    uploaded_file.getvalue(),
                    sanitize_filename(uploaded_file.name),
                    mode,
                    threshold
                )
                
                status.update(label="✅ Complete!", state="complete")
            
            # Results
            if result.get('success'):
                decision = result.get('decision')
                
                if decision == 'APPROVE':
                    success_box(f"✅ **APPROVED** - Risk: {result.get('risk_score', 0)}")
                elif decision == 'BLOCK':
                    error_box(f"🚫 **BLOCKED** - Risk: {result.get('risk_score', 0)}")
                else:
                    warning_box(f"⚠️ **REVIEW** - Risk: {result.get('risk_score', 0)}")
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Risk Score", f"{result.get('risk_score', 0)}/100")
                col2.metric("Confidence", f"{result.get('confidence', 0)*100:.1f}%")
                col3.metric("Duration", f"{result.get('total_duration_ms', 0):.0f}ms")
                
                # Details
                with st.expander("🔍 Details"):
                    st.json(result.get('metadata', {}))
            else:
                error_box(f"❌ Error: {result.get('error')}")

else:
    st.info("👆 Upload a file to get started")