import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def xray_trace_viewer(trace: Dict[str, Any]):
    """
    Display detailed X-Ray trace with timeline visualization
    
    Args:
        trace: X-Ray trace data dict
    """
    
    if not trace:
        st.warning("No trace data available")
        return
    
    trace_id = trace.get('id', 'UNKNOWN')
    timestamp = trace.get('timestamp', '')
    duration = trace.get('duration', 0)
    status = trace.get('status', 'UNKNOWN')
    segments = trace.get('segments', [])
    
    # Trace header
    st.markdown(f"### 🔍 Trace: `{trace_id}`")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", f"{duration}ms")
    
    with col2:
        status_color = "🟢" if status == "SUCCESS" else "🔴"
        st.metric("Status", f"{status_color} {status}")
    
    with col3:
        st.metric("Segments", len(segments))
    
    with col4:
        st.metric("Timestamp", timestamp.split('T')[0] if 'T' in timestamp else timestamp)
    
    st.divider()
    
    # Render visualization
    if segments:
        _render_timeline(segments, duration, trace_id)
        st.divider()
        _render_segment_table(segments)
        st.divider()
        _render_flame_graph(segments, duration)
    else:
        st.info("No segment data available for this trace")


def _render_timeline(segments: List[Dict], total_duration: float, trace_id: str):
    """Render horizontal timeline visualization"""
    
    st.markdown("#### ⏱️ Timeline View")
    
    fig = go.Figure()
    
    # Sort segments by start time
    sorted_segments = sorted(
        segments,
        key=lambda x: x.get('start_time', 0)
    )
    
    # Calculate start time for each segment (cumulative)
    current_time = 0
    y_positions = []
    
    for i, segment in enumerate(sorted_segments):
        seg_name = segment.get('name', f'Segment {i}')
        seg_duration = segment.get('duration', 0)
        seg_status = segment.get('status', 'OK')
        
        # Color based on status
        color = '#00d68f' if seg_status == 'OK' else '#ff5252'
        
        # Add horizontal bar
        fig.add_trace(go.Bar(
            name=seg_name,
            x=[seg_duration],
            y=[seg_name],
            orientation='h',
            marker=dict(
                color=color,
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            hovertemplate=(
                f"<b>{seg_name}</b><br>"
                f"Duration: {seg_duration}ms<br>"
                f"Status: {seg_status}<br>"
                "<extra></extra>"
            ),
            showlegend=False
        ))
        
        y_positions.append(seg_name)
    
    # Update layout
    fig.update_layout(
        title=f"Execution Timeline - {trace_id}",
        xaxis_title="Duration (ms)",
        yaxis_title="Segment",
        height=max(400, len(segments) * 40),
        barmode='overlay',
        template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white',
        showlegend=False,
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_segment_table(segments: List[Dict]):
    """Render detailed segment table"""
    
    st.markdown("#### 📋 Segment Details")
    
    # Build table HTML
    table_html = """
    <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: rgba(74, 158, 255, 0.1); border-bottom: 2px solid #4A9EFF;">
                    <th style="padding: 1rem; text-align: left;">Segment</th>
                    <th style="padding: 1rem; text-align: right;">Duration</th>
                    <th style="padding: 1rem; text-align: center;">Status</th>
                    <th style="padding: 1rem; text-align: right;">% of Total</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Calculate total duration
    total_duration = sum(s.get('duration', 0) for s in segments)
    
    for segment in segments:
        name = segment.get('name', 'Unknown')
        duration = segment.get('duration', 0)
        status = segment.get('status', 'UNKNOWN')
        percentage = (duration / total_duration * 100) if total_duration > 0 else 0
        
        status_color = '#00d68f' if status == 'OK' else '#ff5252'
        status_icon = '✅' if status == 'OK' else '❌'
        
        table_html += f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 0.875rem;">{name}</td>
                <td style="padding: 0.875rem; text-align: right;">{duration}ms</td>
                <td style="padding: 0.875rem; text-align: center;">
                    <span style="color: {status_color};">{status_icon} {status}</span>
                </td>
                <td style="padding: 0.875rem; text-align: right;">{percentage:.1f}%</td>
            </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)


def _render_flame_graph(segments: List[Dict], total_duration: float):
    """Render flame graph visualization"""
    
    st.markdown("#### 🔥 Flame Graph")
    
    # Calculate percentages
    data = []
    labels = []
    parents = []
    values = []
    colors = []
    
    # Root
    labels.append("Total")
    parents.append("")
    values.append(total_duration)
    colors.append('#4A9EFF')
    
    # Segments
    for segment in segments:
        name = segment.get('name', 'Unknown')
        duration = segment.get('duration', 0)
        status = segment.get('status', 'OK')
        
        labels.append(name)
        parents.append("Total")
        values.append(duration)
        colors.append('#00d68f' if status == 'OK' else '#ff5252')
    
    # Create sunburst chart
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Duration: %{value}ms<br>"
            "Percentage: %{percentParent}<br>"
            "<extra></extra>"
        )
    ))
    
    fig.update_layout(
        title="Performance Distribution",
        height=500,
        template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def xray_trace_comparison(traces: List[Dict[str, Any]]):
    """
    Compare multiple X-Ray traces
    
    Args:
        traces: List of trace dicts to compare
    """
    
    if not traces or len(traces) < 2:
        st.warning("Need at least 2 traces for comparison")
        return
    
    st.markdown("### 📊 Trace Comparison")
    
    # Comparison metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_duration = sum(t.get('duration', 0) for t in traces) / len(traces)
        st.metric("Avg Duration", f"{avg_duration:.0f}ms")
    
    with col2:
        success_rate = sum(1 for t in traces if t.get('status') == 'SUCCESS') / len(traces) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col3:
        max_duration = max(t.get('duration', 0) for t in traces)
        st.metric("Max Duration", f"{max_duration}ms")
    
    # Duration distribution
    fig = go.Figure()
    
    trace_ids = [t.get('id', f'Trace {i}') for i, t in enumerate(traces)]
    durations = [t.get('duration', 0) for t in traces]
    
    fig.add_trace(go.Bar(
        x=trace_ids,
        y=durations,
        marker=dict(
            color=durations,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Duration (ms)")
        ),
        hovertemplate="<b>%{x}</b><br>Duration: %{y}ms<extra></extra>"
    ))
    
    fig.update_layout(
        title="Duration Comparison",
        xaxis_title="Trace ID",
        yaxis_title="Duration (ms)",
        height=400,
        template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
