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
    delta_color = "#00d68f" if delta and not delta.startswith("-") else "#ff5252"
    
    card_html = f"""
        <div style="background: linear-gradient(135deg, rgba(74, 158, 255, 0.1), rgba(0, 212, 255, 0.05)); border: 1px solid rgba(74, 158, 255, 0.2); border-radius: 12px; padding: 1.5rem; text-align: center; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 0.875rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                {title}
                {f'<span style="opacity: 0.5; margin-left: 0.5rem;">ℹ️</span>' if help_text else ''}
            </div>
            <div style="font-size: 2rem; font-weight: 900; margin: 0.5rem 0;">
                {prefix}{value}{suffix}
            </div>
            {f'<div style="color: {delta_color}; font-size: 0.875rem; font-weight: 700;">{delta}</div>' if delta else ''}
        </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def metric_card_group(metrics: List[Dict[str, Any]]):
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
    if format_type == 'currency':
        formatted_value = format_currency(value)
    elif format_type == 'percentage':
        formatted_value = format_percentage(value)
    else:
        formatted_value = format_number(int(value))
    
    variant_colors = {
        'primary': '#4A9EFF',
        'success': '#00d68f',
        'warning': '#ffab00',
        'danger':  '#ff5252'
    }
    border_color = variant_colors.get(variant, variant_colors['primary'])
    
    delta_html = ""
    if delta is not None:
        delta_sign  = "+" if delta >= 0 else ""
        delta_color = "#00d68f" if delta >= 0 else "#ff5252"
        delta_arrow = "↗" if delta >= 0 else "↘"
        delta_html = f"""
            <div style="color: {delta_color}; font-size: 0.875rem; font-weight: 700; margin-top: 0.5rem;">
                {delta_arrow} {delta_sign}{delta:.1f}%
            </div>
        """
    
    progress_html = ""
    if target is not None and target > 0:
        progress_pct   = min((value / target) * 100, 100)
        progress_color = "#00d68f" if progress_pct >= 100 else "#4A9EFF"
        progress_html  = f"""
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.5rem; opacity: 0.7;">
                    <span>Progress to Target</span>
                    <span>{progress_pct:.1f}%</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 8px; overflow: hidden;">
                    <div style="background: {progress_color}; height: 100%; width: {progress_pct}%; border-radius: 10px; transition: width 0.5s ease;"></div>
                </div>
            </div>
        """
    
    kpi_html = f"""
        <div style="background: linear-gradient(135deg, rgba(74, 158, 255, 0.15), rgba(0, 212, 255, 0.05)); border: 2px solid {border_color}; border-radius: 12px; padding: 1.5rem; min-height: 140px;">
            <div style="font-size: 0.875rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                {title}
            </div>
            <div style="font-size: 2.5rem; font-weight: 900; line-height: 1; margin-bottom: 0.5rem;">
                {formatted_value}
            </div>
            {delta_html}
            {progress_html}
        </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)