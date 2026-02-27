import streamlit as st
from components.ui_helpers import page_header

def gap(size="1rem"):
    st.markdown(f'<div style="height:{size}"></div>', unsafe_allow_html=True)

def section_header(icon, title, subtitle=None):
    TEXT = '#f1f5f9' if st.session_state.get('theme','dark')=='dark' else '#0f172a'
    TEXT2 = '#94a3b8' if st.session_state.get('theme','dark')=='dark' else '#64748b'
    st.markdown(f"""<div style="margin:1.25rem 0 0.5rem;">
  <div style="font-size:1.05rem;font-weight:700;color:{TEXT};display:flex;align-items:center;gap:.4rem;">{icon} {title}</div>
  {f'<div style="font-size:.8rem;color:{TEXT2};margin-top:2px;">{subtitle}</div>' if subtitle else ''}
</div>""", unsafe_allow_html=True)


def render():
    from components.widgets import alert_box, success_box, error_box, warning_box
    from services.data_provider import process_invoice
    from utils.validators import validate_file_upload
    from utils.helpers import sanitize_filename
    import time

    page_header("📄", "Upload Invoice", "Upload and analyze invoices")

    # Upload section
    st.markdown("### 📤 Upload File")

    col1, col2 = st.columns([2, 1], gap="medium")

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
                    col1, col2, col3 = st.columns(3, gap="medium")
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
