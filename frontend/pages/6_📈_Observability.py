import streamlit as st
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.warning('⚠️ Vui lòng đăng nhập để tiếp tục.')
    st.stop()
from components.widgets import (
    alert_box,
    card_container,
    timeline_item,
    data_table,
    empty_state,
    progress_bar_animated
)
from components.metrics import metric_card_group, kpi_card
from services.data_provider import get_data_provider
from utils.helpers import format_number
import logging
import random

logger = logging.getLogger(__name__)

# Page header
st.markdown('<h1 class="main-header">📈 Observability & Monitoring</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">X-Ray traces and performance monitoring</p>', unsafe_allow_html=True)

# Check backend
provider = get_data_provider()
if not provider.backend_available:
    alert_box("⚠️ Backend unavailable. Showing demo observability data.", "warning")

# Load traces
with st.spinner("Loading traces..."):
    try:
        traces = provider.get_xray_traces(limit=10)
    except Exception as e:
        logger.error(f"Error loading traces: {e}")
        traces = []

# System health overview
st.markdown("### 🏥 System Health")

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card(
        title="System Uptime",
        value=99.95,
        format_type='percentage',
        delta=0.02,
        target=99.9,
        variant='success'
    )

with col2:
    kpi_card(
        title="Avg Response Time",
        value=245,
        format_type='number',
        delta=-12.5,
        variant='primary'
    )

with col3:
    kpi_card(
        title="Error Rate",
        value=0.15,
        format_type='percentage',
        delta=-0.05,
        variant='success'
    )

with col4:
    kpi_card(
        title="Active Requests",
        value=42,
        format_type='number',
        delta=5,
        variant='primary'
    )

st.divider()

# Performance metrics
st.markdown("### ⚡ Performance Metrics")

metric_card_group([
    {'title': 'P50 Latency', 'value': '187ms', 'delta': '-8ms'},
    {'title': 'P95 Latency', 'value': '534ms', 'delta': '-15ms'},
    {'title': 'P99 Latency', 'value': '1.2s', 'delta': '-200ms'},
    {'title': 'Throughput', 'value': '450/min', 'delta': '+25/min'}
])

st.divider()

# X-Ray traces
st.markdown("### 🔍 Recent X-Ray Traces")

if not traces:
    empty_state(
        message="No traces available",
        icon="📊",
        action_text="Refresh",
        action_callback=lambda: st.rerun()
    )
else:
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            options=['All', 'SUCCESS', 'ERROR', 'TIMEOUT'],
            index=0
        )
    
    with col2:
        min_duration = st.number_input(
            "Min Duration (ms)",
            min_value=0,
            value=0,
            step=100
        )
    
    with col3:
        max_traces = st.slider(
            "Show traces",
            min_value=5,
            max_value=50,
            value=10
        )
    
    # Display traces
    for i, trace in enumerate(traces[:max_traces]):
        trace_id = trace.get('id', f'TRACE-{i}')
        timestamp = trace.get('timestamp', '')
        duration = trace.get('duration', 0)
        status = trace.get('status', 'UNKNOWN')
        segments = trace.get('segments', [])
        
        # Apply filters
        if status_filter != 'All' and status != status_filter:
            continue
        
        if duration < min_duration:
            continue
        
        variant = 'success' if status == 'SUCCESS' else 'danger'
        
        with st.expander(
            f"{'✅' if status == 'SUCCESS' else '❌'} {trace_id} - {duration}ms - {timestamp}",
            expanded=False
        ):
            # Trace summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Duration", f"{duration}ms")
            
            with col2:
                st.metric("Segments", len(segments))
            
            with col3:
                st.metric("Status", status)
            
            st.markdown("---")
            
            # Segment breakdown
            st.markdown("**Segment Timeline**")
            
            if segments:
                for segment in segments:
                    seg_name = segment.get('name', 'Unknown')
                    seg_duration = segment.get('duration', 0)
                    seg_status = segment.get('status', 'OK')
                    
                    # Calculate percentage of total
                    percentage = (seg_duration / duration * 100) if duration > 0 else 0
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{seg_name}** - {seg_duration}ms")
                        progress_bar_animated(
                            percentage,
                            100,
                            show_percentage=False,
                            color='success' if seg_status == 'OK' else 'danger'
                        )
                    
                    with col2:
                        st.markdown(f"{percentage:.1f}%")
            
            else:
                st.info("No segment data available")
            
            # HTTP details
            http_method = trace.get('http_method', 'POST')
            http_status = trace.get('http_status', 200)
            url = trace.get('url', '/api/analyze')
            
            st.markdown("---")
            st.markdown("**Request Details**")
            st.code(f"{http_method} {url} - HTTP {http_status}")

st.divider()

# CloudWatch integration
st.markdown("### ☁️ CloudWatch Metrics")

tab1, tab2, tab3 = st.tabs(["API Gateway", "Lambda", "Database"])

with tab1:
    with card_container("API Gateway Metrics", "🌐", variant='primary'):
        st.markdown("**Request Metrics (Last 1 Hour)**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Requests", "4,523", "+12%")
        
        with col2:
            st.metric("4xx Errors", "23", "-5%")
        
        with col3:
            st.metric("5xx Errors", "7", "-2")
        
        st.markdown("---")
        
        # Mock chart data
        import pandas as pd
        import plotly.graph_objects as go
        
        times = pd.date_range(end=pd.Timestamp.now(), periods=12, freq='5T')
        requests = [random.randint(350, 450) for _ in range(12)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=requests,
            mode='lines+markers',
            name='Requests/5min',
            line=dict(color='#4A9EFF', width=3)
        ))
        
        fig.update_layout(
            title='Request Volume',
            xaxis_title='Time',
            yaxis_title='Requests',
            height=300,
            template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    with card_container("Lambda Metrics", "λ", variant='warning'):
        st.markdown("**Function Performance (Last 1 Hour)**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Invocations", "3,892", "+8%")
        
        with col2:
            st.metric("Avg Duration", "2.3s", "-200ms")
        
        with col3:
            st.metric("Errors", "12", "-3")
        
        st.markdown("---")
        
        # Mock duration chart
        durations = [random.randint(1800, 2800) for _ in range(12)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=durations,
            mode='lines+markers',
            name='Duration (ms)',
            line=dict(color='#ffab00', width=3)
        ))
        
        fig.update_layout(
            title='Function Duration',
            xaxis_title='Time',
            yaxis_title='Duration (ms)',
            height=300,
            template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    with card_container("Database Metrics", "🗄️", variant='success'):
        st.markdown("**RDS Performance (Last 1 Hour)**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("CPU Usage", "42%", "-8%")
        
        with col2:
            st.metric("Connections", "28", "+3")
        
        with col3:
            st.metric("Query Time", "15ms", "-2ms")
        
        st.markdown("---")
        
        # Mock connection chart
        connections = [random.randint(20, 35) for _ in range(12)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=connections,
            mode='lines+markers',
            name='Active Connections',
            line=dict(color='#00d68f', width=3)
        ))
        
        fig.update_layout(
            title='Database Connections',
            xaxis_title='Time',
            yaxis_title='Connections',
            height=300,
            template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Alerts & anomalies
st.markdown("### 🚨 Alerts & Anomalies")

with card_container("Recent Alerts", "⚠️", variant='warning'):
    alerts = [
        {
            'title': 'High Latency Detected',
            'description': 'P99 latency exceeded 2s threshold',
            'timestamp': '5 minutes ago',
            'severity': 'WARNING'
        },
        {
            'title': 'Database Connection Pool Near Limit',
            'description': '45/50 connections in use',
            'timestamp': '15 minutes ago',
            'severity': 'WARNING'
        },
        {
            'title': 'Error Rate Spike',
            'description': '5xx errors increased by 50%',
            'timestamp': '1 hour ago',
            'severity': 'HIGH'
        }
    ]
    
    for alert in alerts:
        timeline_item(
            title=alert['title'],
            description=alert['description'],
            timestamp=alert['timestamp'],
            status='warning' if alert['severity'] == 'WARNING' else 'error'
        )