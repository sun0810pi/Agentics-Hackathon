import streamlit as st
from typing import Optional, List, Dict, Any
from utils.helpers import format_currency, format_percentage, format_number


def metric_card(
    title: str,
    value: Any,
    delta: Optional[str] = None,
    prefix: str = "",
    suffix: str = "",
    help_text: Optional[str] = None
):
    """
    Display a single metric card
    
    Args:
        title: Metric title
        value: Metric value
        delta: Change indicator (e.g., "+5.2%")
        prefix: Prefix for value (e.g., "$")
        suffix: Suffix for value (e.g., "%")
        help_text: Help tooltip text
    """
    delta_color = "metric-delta"
    if delta and delta.startswith("-"):
        delta_color = "metric-delta negative"
    
    card_html = f"""
        <div class="metric-card">
            <div class="metric-title">
                {title}
                {f'<span style="opacity: 0.5; margin-left: 0.5rem;">ℹ️</span>' if help_text else ''}
            </div>
            <div class="metric-value">
                {prefix}{value}{suffix}
            </div>
            {f'<div class="{delta_color}">{delta}</div>' if delta else ''}
        </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def metric_card_group(metrics: List[Dict[str, Any]]):
    """
    Display a group of metric cards in columns
    
    Args:
        metrics: List of metric dicts with keys: title, value, delta, prefix, suffix
    """
    if not metrics:
        return
    
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            metric_card(
                title=metric.get('title', ''),
                value=metric.get('value', 0),
                delta=metric.get('delta'),
                prefix=metric.get('prefix', ''),
                suffix=metric.get('suffix', ''),
                help_text=metric.get('help_text')
            )


def kpi_card(
    title: str,
    value: float,
    format_type: str = 'number',
    delta: Optional[float] = None,
    target: Optional[float] = None,
    variant: str = 'primary'
):
    """
    Advanced KPI card with formatting and comparison
    
    Args:
        title: KPI title
        value: KPI value
        format_type: 'number', 'currency', 'percentage'
        delta: Change from previous period (percentage)
        target: Target value for comparison
        variant: 'primary', 'success', 'warning', 'danger'
    """
    # Format value based on type
    if format_type == 'currency':
        formatted_value = format_currency(value)
    elif format_type == 'percentage':
        formatted_value = format_percentage(value)
    else:
        formatted_value = format_number(value)
    
    # Calculate delta display
    delta_html = ""
    if delta is not None:
        delta_sign = "+" if delta >= 0 else ""
        delta_color = "#00d68f" if delta >= 0 else "#ff5252"
        delta_html = f"""
            <div style="color: {delta_color}; font-size: 0.875rem; font-weight: 700; margin-top: 0.5rem;">
                {delta_sign}{delta:.1f}% vs last period
            </div>
        """
    
    # Calculate target comparison
    target_html = ""
    if target is not None:
        progress = (value / target) * 100 if target > 0 else 0
        target_color = "#00d68f" if progress >= 100 else "#ffab00"
        target_html = f"""
            <div style="margin-top: 0.75rem;">
                <div style="font-size: 0.75rem; opacity: 0.7; margin-bottom: 0.25rem;">
                    Target: {format_number(target)}
                </div>
                <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="background: {target_color}; height: 100%; width: {min(progress, 100)}%; transition: width 0.5s ease;"></div>
                </div>
            </div>
        """
    
    # Variant colors
    variant_colors = {
        'primary': '#4A9EFF',
        'success': '#00d68f',
        'warning': '#ffab00',
        'danger': '#ff5252'
    }
    
    border_color = variant_colors.get(variant, '#4A9EFF')
    
    card_html = f"""
        <div class="metric-card metric-card-{variant}" style="border-left: 4px solid {border_color};">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{formatted_value}</div>
            {delta_html}
            {target_html}
        </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)