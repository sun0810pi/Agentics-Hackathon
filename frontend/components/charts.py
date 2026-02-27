import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import streamlit as st


def plot_time_series(
    data: List[Dict[str, Any]],
    title: str = "Processing Volume Over Time",
    height: int = 400
):
    """
    Plot time series chart
    
    Args:
        data: List of dicts with 'date' and metric keys
        title: Chart title
        height: Chart height in pixels
    """
    if not data:
        st.warning("No data available for time series chart")
        return
    
    dates = [d['date'] for d in data]
    processed = [d.get('processed', 0) for d in data]
    approved = [d.get('approved', 0) for d in data]
    blocked = [d.get('blocked', 0) for d in data]
    
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=dates, y=processed,
        name='Total Processed',
        mode='lines+markers',
        line=dict(color='#4A9EFF', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Processed: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=approved,
        name='Approved',
        mode='lines+markers',
        line=dict(color='#00d68f', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x}</b><br>Approved: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=blocked,
        name='Blocked',
        mode='lines+markers',
        line=dict(color='#ff5252', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x}</b><br>Blocked: %{y}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Count',
        height=height,
        hovermode='x unified',
        template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_risk_distribution(
    data: List[Dict[str, Any]],
    title: str = "Risk Score Distribution",
    height: int = 400
):
    """
    Plot risk distribution pie chart
    
    Args:
        data: List of dicts with 'risk_level', 'count', 'pct'
        title: Chart title
        height: Chart height
    """
    if not data:
        st.warning("No data available for risk distribution chart")
        return
    
    labels = [d.get('risk_level', 'UNKNOWN') for d in data]
    values = [d.get('count', 0) for d in data]
    
    colors = {
        'LOW': '#00d68f',
        'MEDIUM': '#ffab00',
        'HIGH': '#ff5252',
        'CRITICAL': '#dc2626'
    }
    
    color_list = [colors.get(label, '#718096') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=color_list),
        textinfo='label+percent',
        textfont=dict(size=14),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=title,
        height=height,
        template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_agent_performance(
    agents: List[Dict[str, Any]],
    title: str = "Agent Performance Metrics",
    height: int = 500
):
    """
    Plot agent performance bar chart
    
    Args:
        agents: List of agent dicts with metrics
        title: Chart title
        height: Chart height
    """
    if not agents:
        st.warning("No agent data available")
        return
    
    names = [a.get('name', f"Agent {a.get('id', '?')}") for a in agents]
    success_rates = [a.get('success_rate', 0) for a in agents]
    latencies = [a.get('avg_latency_ms', 0) for a in agents]
    
    # Create subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Success Rate (%)', 'Avg Latency (ms)'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Success rate
    fig.add_trace(
        go.Bar(
            x=names,
            y=success_rates,
            name='Success Rate',
            marker=dict(color='#00d68f'),
            hovertemplate='<b>%{x}</b><br>Success Rate: %{y:.1f}%<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Latency
    fig.add_trace(
        go.Bar(
            x=names,
            y=latencies,
            name='Latency',
            marker=dict(color='#4A9EFF'),
            hovertemplate='<b>%{x}</b><br>Latency: %{y:.0f}ms<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title=title,
        height=height,
        showlegend=False,
        template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white',
    )
    
    fig.update_xaxes(tickangle=-45)
    
    st.plotly_chart(fig, use_container_width=True)


def plot_fraud_by_type(
    scenarios: List[Dict[str, Any]],
    title: str = "Fraud Detection by Type",
    height: int = 400
):
    """
    Plot fraud scenarios by type
    
    Args:
        scenarios: List of fraud scenario dicts
        title: Chart title
        height: Chart height
    """
    if not scenarios:
        st.warning("No fraud scenarios data available")
        return
    
    # Group by type
    type_counts = {}
    type_amounts = {}
    
    for scenario in scenarios:
        fraud_type = scenario.get('type', 'Unknown')
        type_counts[fraud_type] = type_counts.get(fraud_type, 0) + 1
        type_amounts[fraud_type] = type_amounts.get(fraud_type, 0) + scenario.get('potential_loss', 0)
    
    types = list(type_counts.keys())
    counts = list(type_counts.values())
    amounts = [type_amounts[t] for t in types]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=types,
        y=counts,
        name='Count',
        marker=dict(color='#ff5252'),
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=types,
        y=amounts,
        name='Potential Loss ($)',
        mode='lines+markers',
        marker=dict(color='#ffab00', size=10),
        line=dict(color='#ffab00', width=3),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Loss: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis=dict(title='Fraud Type', tickangle=-45),
        yaxis=dict(title='Count', side='left'),
        yaxis2=dict(title='Potential Loss ($)', side='right', overlaying='y'),
        template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)