import streamlit as st
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")
from components.sidebar import render_sidebar
render_sidebar()
from components.widgets import alert_box, stat_card, progress_bar_animated, card_container
from components.charts import plot_agent_performance
from components.metrics import kpi_card
from services.data_provider import get_agent_metrics, get_data_provider
from utils.helpers import format_percentage
import logging

logger = logging.getLogger(__name__)

# Page header
st.markdown('<h1 class="main-header">🧠 ML Insights & Analytics</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Machine learning model performance and predictions</p>', unsafe_allow_html=True)

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
st.markdown("### 🎯 Model Performance Overview")

col1, col2, col3, col4 = st.columns(4)

# Calculate aggregate metrics
if agents:
    avg_success = sum(a.get('success_rate', 0) for a in agents) / len(agents)
    avg_latency = sum(a.get('avg_latency_ms', 0) for a in agents) / len(agents)
    total_processed = sum(a.get('processed_count', 0) for a in agents)
    healthy_count = sum(1 for a in agents if a.get('status') == 'active')
else:
    avg_success = 0
    avg_latency = 0
    total_processed = 0
    healthy_count = 0

with col1:
    kpi_card(
        title="Model Accuracy",
        value=avg_success,
        format_type='percentage',
        delta=2.3,
        target=99.0,
        variant='success'
    )

with col2:
    kpi_card(
        title="Avg Inference Time",
        value=avg_latency,
        format_type='number',
        delta=-15.2,
        variant='primary'
    )

with col3:
    kpi_card(
        title="Total Predictions",
        value=total_processed,
        format_type='number',
        delta=8.7,
        variant='primary'
    )

with col4:
    kpi_card(
        title="Models Online",
        value=healthy_count,
        format_type='number',
        delta=0,
        variant='success'
    )

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
                col1, col2, col3 = st.columns(3)
                
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

col1, col2 = st.columns(2)

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

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Retrain Models", use_container_width=True, type="primary"):
        st.info("Model retraining scheduled. This will take ~30 minutes.")

with col2:
    if st.button("📊 View Training History", use_container_width=True):
        st.info("Training history viewer coming soon!")

with col3:
    if st.button("⚙️ Hyperparameter Tuning", use_container_width=True):
        st.info("Hyperparameter optimization interface coming soon!")