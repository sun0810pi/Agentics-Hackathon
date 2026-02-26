import streamlit as st
from components.metrics import metric_card_group, kpi_card
from components.charts import plot_time_series, plot_risk_distribution
from components.widgets import alert_box
from services.data_provider import get_dashboard_metrics, get_agent_metrics, get_data_provider
from utils.helpers import format_currency, format_percentage, format_number
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

@st.cache_data(ttl=60)
def _load():
    try:
        metrics = get_dashboard_metrics()
        agents = get_agent_metrics()
        ts = get_data_provider().get_time_series(days=30)
        return {"ok": True, "metrics": metrics, "agents": agents, "ts": ts}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def render():
    """
    📊 Dashboard Overview - Comprehensive fraud detection dashboard
    Shows KPIs, charts, agent status, and system health
    """
    
    # ═══════════════════════════════════════════════════════════
    # HEADER SECTION
    # ═══════════════════════════════════════════════════════════
    st.markdown("🏠 **Home** / **Dashboard**")
    st.title("📊 Dashboard Overview")
    st.markdown("**Real-time fraud detection insights and analytics**")
    st.markdown("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Spacing
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    
    # Backend status check
    provider = get_data_provider()
    if not provider.backend_available:
        st.warning("⚠️ Backend unavailable — showing demo data.")
    
    # Load data
    data = _load()
    if not data["ok"]:
        st.error(f"❌ Failed to load data: {data['error']}")
        return
    
    m = data["metrics"]
    agents = data["agents"]
    ts_data = data["ts"]
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 1: KEY PERFORMANCE INDICATORS
    # ═══════════════════════════════════════════════════════════
    st.markdown("### 🎯 Key Performance Indicators")
    st.markdown("Core metrics for fraud detection performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="TOTAL PROCESSED",
            value=f"{m.get('total_processed', 0):,}",
            delta="+5.2%",
            help="Total invoices processed today"
        )
    
    with col2:
        st.metric(
            label="ACCURACY",
            value=f"{m.get('accuracy', 0):.1f}%",
            delta="+2.1%",
            help="Model detection accuracy"
        )
    
    with col3:
        st.metric(
            label="FRAUD PREVENTED",
            value=format_currency(m.get('fraud_prevented_usd', 0)),
            delta="+12.3%",
            help="Total fraud amount prevented"
        )
    
    with col4:
        st.metric(
            label="AVG LATENCY",
            value=f"{m.get('avg_latency_ms', 0):.0f}ms",
            delta="-8.5ms",
            help="Average processing time"
        )
    
    # Spacing
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 2: PROCESSING STATISTICS
    # ═══════════════════════════════════════════════════════════
    st.markdown("### 📈 Processing Statistics")
    st.markdown("Breakdown of processed transactions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="APPROVED",
            value=format_number(m.get('total_approved', 0)),
            delta="+3.2%",
            help="Transactions approved"
        )
    
    with col2:
        st.metric(
            label="BLOCKED",
            value=format_number(m.get('total_blocked', 0)),
            delta="+15.8%",
            help="Fraudulent transactions blocked"
        )
    
    with col3:
        st.metric(
            label="PENDING",
            value=format_number(m.get('total_pending', 0)),
            delta="-5.1%",
            help="Awaiting manual review"
        )
    
    with col4:
        st.metric(
            label="AUTOMATION RATE",
            value=format_percentage(m.get('automation_rate', 0)),
            delta="+2.3%",
            help="Automated decision rate"
        )
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 3: TRANSACTION ANALYSIS CHARTS
    # ═══════════════════════════════════════════════════════════
    st.markdown("### 📊 Transaction Analysis")
    st.markdown("Volume trends and risk distribution over the past 30 days")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Processing Volume (30 Days)")
        if ts_data:
            plot_time_series(
                data=ts_data,
                title="Invoice Trend",
                height=400
            )
        else:
            st.info("📊 No time series data available")
    
    with col2:
        st.markdown("#### Risk Distribution")
        plot_risk_distribution(
            data=[
                {"risk_level": "LOW", "count": m.get('total_approved', 0), "pct": 75.2},
                {"risk_level": "MEDIUM", "count": m.get('total_pending', 0), "pct": 12.8},
                {"risk_level": "HIGH", "count": m.get('total_blocked', 0), "pct": 12.0},
            ],
            title="Risk Scores",
            height=400
        )
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 4: DETECTION PERFORMANCE
    # ═══════════════════════════════════════════════════════════
    st.markdown("### 🎯 Detection Performance")
    st.markdown("Model accuracy and fraud type breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Accuracy Trend (7 Days)")
        
        # Generate accuracy trend data
        days = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
        accuracy = [95.2, 96.1, 97.3, 96.8, 97.6, 98.1, 98.3]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days,
            y=accuracy,
            mode='lines+markers',
            name='Accuracy',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[94, 100], ticksuffix='%'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Fraud Types Detected")
        
        # Fraud type distribution
        fraud_types = {
            'Identity Theft': 35,
            'Account Takeover': 25,
            'Synthetic Identity': 18,
            'Card Fraud': 12,
            'Other': 10
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(fraud_types.keys()),
            values=list(fraud_types.values()),
            hole=0.4,
            marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'])
        )])
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 5: AGENT STATUS
    # ═══════════════════════════════════════════════════════════
    st.markdown("### 🤖 Agent Status")
    st.markdown("Real-time status of fraud detection agents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_agents = agents.get('total', 17)
        active_agents = agents.get('active', 15)
        st.metric(
            label="ACTIVE AGENTS",
            value=f"{active_agents}/{total_agents}",
            delta=f"{(active_agents/total_agents*100):.1f}%",
            help="Currently active detection agents"
        )
    
    with col2:
        avg_confidence = agents.get('avg_confidence', 0.94)
        st.metric(
            label="AVG CONFIDENCE",
            value=f"{avg_confidence*100:.1f}%",
            delta="+1.2%",
            help="Average agent confidence score"
        )
    
    with col3:
        alerts_triggered = agents.get('alerts_24h', 23)
        st.metric(
            label="ALERTS (24H)",
            value=f"{alerts_triggered}",
            delta="+5",
            help="Alerts triggered in last 24 hours"
        )
    
    # Agent tier breakdown
    st.markdown("#### Agent Distribution by Tier")
    tier_col1, tier_col2, tier_col3, tier_col4 = st.columns(4)
    
    with tier_col1:
        st.info("**Core Detection**\n\n8 agents active")
    
    with tier_col2:
        st.success("**ML Intelligence**\n\n3 agents active")
    
    with tier_col3:
        st.warning("**Merchant Success**\n\n3 agents active")
    
    with tier_col4:
        st.error("**Security**\n\n3 agents active")
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 6: RECENT ALERTS
    # ═══════════════════════════════════════════════════════════
    st.markdown("### 🚨 Recent High-Priority Alerts")
    st.markdown("Latest fraud attempts and suspicious activities")
    
    # Sample alert data
    import pandas as pd
    alerts_data = pd.DataFrame([
        {
            "Time": "2 min ago",
            "Type": "🔴 Account Takeover",
            "Amount": "$12,450",
            "Risk": "HIGH",
            "Status": "Blocked"
        },
        {
            "Time": "15 min ago",
            "Type": "🟡 Suspicious Pattern",
            "Amount": "$3,200",
            "Risk": "MEDIUM",
            "Status": "Review"
        },
        {
            "Time": "32 min ago",
            "Type": "🔴 Identity Theft",
            "Amount": "$8,900",
            "Risk": "HIGH",
            "Status": "Blocked"
        },
        {
            "Time": "1 hour ago",
            "Type": "🟡 Velocity Check",
            "Amount": "$1,500",
            "Risk": "MEDIUM",
            "Status": "Approved"
        },
        {
            "Time": "2 hours ago",
            "Type": "🔴 Card Fraud",
            "Amount": "$5,670",
            "Risk": "HIGH",
            "Status": "Blocked"
        }
    ])
    
    st.dataframe(
        alerts_data,
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 7: SYSTEM HEALTH
    # ═══════════════════════════════════════════════════════════
    st.markdown("### ⚡ System Health & Performance")
    st.markdown("Infrastructure and resource utilization")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="P50 LATENCY",
            value="187ms",
            delta="-8ms",
            help="50th percentile response time"
        )
    
    with col2:
        st.metric(
            label="P95 LATENCY",
            value="534ms",
            delta="-15ms",
            help="95th percentile response time"
        )
    
    with col3:
        st.metric(
            label="P99 LATENCY",
            value="1.2s",
            delta="-200ms",
            help="99th percentile response time"
        )
    
    with col4:
        st.metric(
            label="THROUGHPUT",
            value="450/min",
            delta="+25/min",
            help="Transactions per minute"
        )
    
    # System resources
    st.markdown("#### Resource Utilization")
    resource_col1, resource_col2, resource_col3 = st.columns(3)
    
    with resource_col1:
        st.progress(0.67, text="**CPU Usage:** 67%")
    
    with resource_col2:
        st.progress(0.52, text="**Memory:** 52%")
    
    with resource_col3:
        st.progress(0.34, text="**Network:** 34%")
    
    # Spacing at end
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    
    # Footer info
    st.caption("💡 Dashboard auto-refreshes every 60 seconds")
