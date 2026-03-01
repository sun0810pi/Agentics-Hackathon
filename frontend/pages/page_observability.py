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
    _D   = st.session_state.get('theme','dark') == 'dark'
    _T   = '#f5f5f5' if _D else '#0a0a0a'
    _T2  = '#a3a3a3' if _D else '#737373'
    _BOR = '#262626' if _D else '#e5e5e5'
    st.markdown(f"""<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:2px solid {_BOR};">
<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem;">
<span style="font-size:1.5rem;line-height:1;">📈</span>
<h1 style="font-family:Syne,sans-serif;font-size:1.75rem;font-weight:800;color:{_T};letter-spacing:-.03em;margin:0;line-height:1.1;">Observability & Monitoring</h1>
</div>
<p style="font-family:JetBrains Mono,monospace;font-size:.72rem;color:#10b981;letter-spacing:.06em;margin:0;text-transform:uppercase;">SUBObservability & Monitoring</p>
</div>""", unsafe_allow_html=True)

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

    col1, col2, col3, col4 = st.columns(4, gap="medium")

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
        col1, col2, col3 = st.columns(3, gap="medium")

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
        _trace_count = 0
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

            _trace_count += 1
            _D = st.session_state.get('theme','dark') == 'dark'
            _ok = status == 'SUCCESS'
            _status_icon = "✅" if _ok else "❌"
            _ts = timestamp[:19].replace('T', ' ') if timestamp and len(timestamp) > 10 else str(timestamp)
            _bor = '#262626' if _D else '#e5e5e5'
            _bg  = '#141414' if _D else '#ffffff'
            _t   = '#f5f5f5' if _D else '#0a0a0a'
            _t2  = '#a3a3a3' if _D else '#737373'
            _status_color = '#10b981' if _ok else '#ef4444'

            # Row display — no expander, use st.container
            with st.container():
                st.markdown(f'''<div style="background:{_bg};border:2px solid {_bor};
padding:.65rem 1rem;margin-bottom:.35rem;display:flex;align-items:center;gap:.75rem;">
  <span style="font-size:.9rem;line-height:1;flex-shrink:0;">{_status_icon}</span>
  <code style="font-family:JetBrains Mono,monospace;font-size:.78rem;color:{_status_color};font-weight:600;flex-shrink:0;">{trace_id}</code>
  <span style="font-family:JetBrains Mono,monospace;font-size:.72rem;color:{_t2};">{duration}ms</span>
  <span style="font-family:JetBrains Mono,monospace;font-size:.65rem;color:{_t2};margin-left:auto;">{_ts}</span>
</div>''', unsafe_allow_html=True)
            variant = 'success' if _ok else 'danger'
            if st.toggle(f"Details — {trace_id}", key=f"trace_tog_{i}", value=False):
                    col1, col2, col3 = st.columns(3, gap="medium")
                    with col1:
                        st.metric("Total Duration", f"{duration}ms")
                    with col2:
                        st.metric("Segments", len(segments))
                    with col3:
                        st.metric("Status", status)
                    st.markdown("---")
                    if segments:
                        st.markdown("**Segment Timeline**")
                        for segment in segments:
                            seg_name = segment.get('name', 'Unknown')
                            seg_duration = segment.get('duration', 0)
                            seg_status = segment.get('status', 'OK')
                            percentage = (seg_duration / duration * 100) if duration > 0 else 0
                            sc1, sc2 = st.columns([3, 1], gap="medium")
                            with sc1:
                                st.markdown(f"**{seg_name}** - {seg_duration}ms")
                                progress_bar_animated(
                                    percentage, 100,
                                    show_percentage=False,
                                    color='success' if seg_status == 'OK' else 'danger'
                                )
                            with sc2:
                                st.markdown(f"{percentage:.1f}%")
                    else:
                        st.info("No segment data available")
                    http_method = trace.get('http_method', 'POST')
                    http_status_code = trace.get('http_status', 200)
                    url = trace.get('url', '/api/analyze')
                    st.markdown("---")
                    st.markdown("**Request Details**")
                    st.code(f"{http_method} {url} - HTTP {http_status_code}")

    st.divider()

    # CloudWatch integration
    st.markdown("### ☁️ CloudWatch Metrics")

    tab1, tab2, tab3 = st.tabs(["API Gateway", "Lambda", "Database"])

    with tab1:
        with card_container("API Gateway Metrics", "🌐", variant='primary'):
            st.markdown("**Request Metrics (Last 1 Hour)**")

            col1, col2, col3 = st.columns(3, gap="medium")

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
                template='plotly_dark' if st.session_state.get('theme','dark')=='dark' else 'plotly_white' if st.session_state.get('theme') == 'dark' else 'plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with card_container("Lambda Metrics", "λ", variant='warning'):
            st.markdown("**Function Performance (Last 1 Hour)**")

            col1, col2, col3 = st.columns(3, gap="medium")

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
                template='plotly_dark' if st.session_state.get('theme','dark')=='dark' else 'plotly_white' if st.session_state.get('theme') == 'dark' else 'plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        with card_container("Database Metrics", "🗄️", variant='success'):
            st.markdown("**RDS Performance (Last 1 Hour)**")

            col1, col2, col3 = st.columns(3, gap="medium")

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
                template='plotly_dark' if st.session_state.get('theme','dark')=='dark' else 'plotly_white' if st.session_state.get('theme') == 'dark' else 'plotly_white'
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
