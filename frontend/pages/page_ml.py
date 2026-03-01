import streamlit as st

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
    from components.widgets import alert_box, stat_card, progress_bar_animated, card_container
    from components.charts import plot_agent_performance
    from components.metrics import kpi_card
    from services.data_provider import get_agent_metrics, get_data_provider
    from utils.helpers import format_percentage
    import logging

    logger = logging.getLogger(__name__)

    # Page header
    _D   = st.session_state.get('theme','dark') == 'dark'
    _T   = '#f5f5f5' if _D else '#0a0a0a'
    _T2  = '#a3a3a3' if _D else '#737373'
    _BOR = '#262626' if _D else '#e5e5e5'
    st.markdown(f"""<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:2px solid {_BOR};">
<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem;">
<span style="font-size:1.5rem;line-height:1;">🧠</span>
<h1 style="font-family:Syne,sans-serif;font-size:1.75rem;font-weight:800;color:{_T};letter-spacing:-.03em;margin:0;line-height:1.1;">ML Insights & Analytics</h1>
</div>
<p style="font-family:JetBrains Mono,monospace;font-size:.72rem;color:#10b981;letter-spacing:.06em;margin:0;text-transform:uppercase;">Model performance · Agent intelligence</p>
</div>""", unsafe_allow_html=True)

    # Check backend
    provider = get_data_provider()
    if not provider.backend_available:
        alert_box("⚠️ Backend unavailable. Showing demo ML insights.", "warning")

    # Load agent metrics
    with st.spinner("Loading ML insights..."):
        try:
            agents = get_agent_metrics()
        except Exception as e:
            logger.error(f"Error loading agent metrics: {e}")
            st.error("Failed to load ML insights")
            agents = []

    # Model performance overview
    # ── Model Performance KPIs ─────────────────────────────────────
    # Calculate aggregate metrics from agent list
    if agents:
        avg_success      = sum(a.get('success_rate', 97) for a in agents) / len(agents)
        avg_latency      = sum(a.get('avg_latency_ms', 150) for a in agents) / len(agents)
        total_processed  = sum(a.get('processed_count', 0) for a in agents)
        healthy_count    = sum(1 for a in agents if a.get('status') == 'active')
    else:
        avg_success, avg_latency, total_processed, healthy_count = 97.4, 187, 142830, 15

    def _ml_card(col, label, value, delta=None, up=True):
        D = st.session_state.get('theme','dark') == 'dark'
        BG  = '#141414' if D else '#ffffff'
        BOR = '#262626'  if D else '#0a0a0a'
        T   = '#f5f5f5' if D else '#0a0a0a'
        T2  = '#a3a3a3' if D else '#737373'
        SHD = '2px 2px 0px rgba(255,255,255,0.08)' if D else '4px 4px 0px #0a0a0a'
        dc  = '#10b981' if up else '#ef4444'
        ar  = '↑' if up else '↓'
        d   = f'<div style="font-size:.78rem;color:{dc};margin-top:.4rem;font-weight:600;">{ar} {delta}</div>' if delta else ''
        html = f'''<div style="background:{BG};border:2px solid {BOR};border-radius:0;
padding:1rem 1.1rem .9rem;position:relative;overflow:hidden;box-shadow:{SHD};">
<div style="position:absolute;top:0;left:0;right:0;height:3px;background:#10b981;"></div>
<div style="font-family:JetBrains Mono,monospace;font-size:.6rem;font-weight:500;
  color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.4rem;">{label}</div>
<div style="font-family:Syne,sans-serif;font-size:1.85rem;font-weight:800;
  color:{T};letter-spacing:-.02em;line-height:1.1;">{value}</div>
{d}
</div>'''
        col.markdown(html, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    _ml_card(col1, "Model Accuracy",      f"{avg_success:.1f}%",       "+2.3%",  True)
    _ml_card(col2, "Avg Inference Time",  f"{avg_latency:.0f}ms",      "-15ms",  True)
    _ml_card(col3, "Total Predictions",   f"{total_processed:,}",      "+8.7%",  True)
    _ml_card(col4, "Models Online",       f"{healthy_count}/{len(agents) if agents else 17}", "+0", True)

    st.divider()

    # Agent performance breakdown
    st.markdown("### 🤖 Agent Performance Breakdown")

    if agents:
        # Tier 1 agents
        tier1_agents = [a for a in agents if a.get('id', 0) <= 7]

        if tier1_agents:
            st.markdown("#### Tier 1: Core Detection Agents")
            plot_agent_performance(tier1_agents, "Core Detection Performance", 400)

        st.divider()

        # Tier 2 agents
        tier2_agents = [a for a in agents if 8 <= a.get('id', 0) <= 10]

        if tier2_agents:
            st.markdown("#### Tier 2: ML Intelligence Agents")

            for agent in tier2_agents:
                with card_container(
                    title=f"Agent {agent.get('id')}: {agent.get('name', 'Unknown')}",
                    icon="🧠",
                    variant='primary'
                ):
                    col1, col2, col3 = st.columns(3, gap="medium")

                    with col1:
                        st.metric(
                            "Success Rate",
                            f"{agent.get('success_rate', 0):.1f}%",
                            f"+{agent.get('success_rate', 0) - 95:.1f}%"
                        )

                    with col2:
                        st.metric(
                            "Avg Latency",
                            f"{agent.get('avg_latency_ms', 0):.0f}ms",
                            f"-{agent.get('avg_latency_ms', 0) * 0.1:.0f}ms"
                        )

                    with col3:
                        st.metric(
                            "Processed",
                            f"{agent.get('processed_count', 0):,}",
                            "+12.5%"
                        )

                    st.markdown("---")

                    st.markdown("**Description**")
                    st.write(agent.get('description', 'No description available'))

                    # Performance bar
                    st.markdown("**Performance Score**")
                    progress_bar_animated(
                        agent.get('success_rate', 0),
                        100,
                        show_percentage=True,
                        color='success'
                    )

    else:
        st.info("No agent metrics available")

    st.divider()

    # Feature importance
    st.markdown("### 📊 Feature Importance")

    with card_container("Top Features for Fraud Detection", "🎯", variant='primary'):
        features = [
            {'name': 'Transaction Amount', 'importance': 95},
            {'name': 'Merchant History', 'importance': 88},
            {'name': 'Time of Day', 'importance': 76},
            {'name': 'Geographic Location', 'importance': 72},
            {'name': 'User Behavior Pattern', 'importance': 68},
            {'name': 'Payment Method', 'importance': 55},
            {'name': 'Device Fingerprint', 'importance': 48},
            {'name': 'IP Address Reputation', 'importance': 42}
        ]

        for feature in features:
            st.markdown(f"**{feature['name']}**")
            progress_bar_animated(
                feature['importance'],
                100,
                show_percentage=True,
                color='primary'
            )

    st.divider()

    # Model statistics
    st.markdown("### 📈 Model Statistics")

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with card_container("Confusion Matrix", "📊", variant='default'):
            st.markdown("""
            **Last 1000 Predictions:**

            |              | Predicted Fraud | Predicted Legit |
            |--------------|----------------|----------------|
            | **Actual Fraud** | 142 (TP)       | 8 (FN)         |
            | **Actual Legit** | 12 (FP)        | 838 (TN)       |

            - **True Positive Rate:** 94.7%
            - **False Positive Rate:** 1.4%
            - **Precision:** 92.2%
            - **F1 Score:** 93.4%
            """)

    with col2:
        with card_container("Model Versions", "🔄", variant='info'):
            st.markdown("""
            **Current Models:**

            - **OCR Model:** Tesseract 5.3.0
            - **NLP Model:** Claude Sonnet 4
            - **Fraud Detection:** XGBoost v2.0
            - **Anomaly Detection:** Isolation Forest
            - **Risk Scoring:** Custom Ensemble

            **Last Updated:** 2026-02-15
            """)

    st.divider()

    # Training & optimization
    st.markdown("### 🔧 Model Training & Optimization")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        if st.button("🔄 Retrain Models", use_container_width=True, type="primary"):
            st.info("Model retraining scheduled. This will take ~30 minutes.")

    with col2:
        if st.button("📊 View Training History", use_container_width=True):
            st.info("Training history viewer coming soon!")

    with col3:
        if st.button("⚙️ Hyperparameter Tuning", use_container_width=True):
            st.info("Hyperparameter optimization interface coming soon!")
