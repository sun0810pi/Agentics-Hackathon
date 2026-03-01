import streamlit as st
from typing import Optional, List, Dict, Any
from utils.helpers import format_currency, format_percentage, format_number


def _nb_card(col_or_st, label, value, delta=None, up=True, subtitle=None):
    """Neo-brutalist metric card — shared helper."""
    D   = st.session_state.get('theme', 'dark') == 'dark'
    BG  = '#141414' if D else '#ffffff'
    BOR = '#262626'  if D else '#0a0a0a'
    T   = '#f5f5f5' if D else '#0a0a0a'
    T2  = '#a3a3a3' if D else '#737373'
    SHD = '2px 2px 0px rgba(255,255,255,0.08)' if D else '4px 4px 0px #0a0a0a'
    dc  = '#10b981' if up else '#ef4444'
    ar  = '↑' if up else '↓'
    d_html = f'<div style="font-size:.75rem;color:{dc};margin-top:.35rem;font-weight:600;">{ar} {delta}</div>' if delta else ''
    sub_html = f'<div style="font-size:.65rem;color:{T2};margin-top:.25rem;">{subtitle}</div>' if subtitle else ''
    html = f'''<div style="background:{BG};border:2px solid {BOR};border-radius:0;
padding:1rem 1.1rem .9rem;position:relative;overflow:hidden;box-shadow:{SHD};margin-bottom:4px;">
<div style="position:absolute;top:0;left:0;right:0;height:3px;background:#10b981;"></div>
<div style="font-family:'JetBrains Mono',monospace;font-size:.6rem;font-weight:500;
  color:{T2};text-transform:uppercase;letter-spacing:.12em;margin-bottom:.35rem;">{label}</div>
<div style="font-family:'Syne',sans-serif;font-size:1.85rem;font-weight:800;
  color:{T};letter-spacing:-.02em;line-height:1.1;">{value}</div>
{d_html}{sub_html}
</div>'''
    target = col_or_st if hasattr(col_or_st, 'markdown') else st
    target.markdown(html, unsafe_allow_html=True)


def metric_card(title, value, delta=None, prefix="", suffix="", help_text=None):
    """Neo-brutalist metric card (compat shim)."""
    up = not (delta and str(delta).startswith('-'))
    _nb_card(st, title, f"{prefix}{value}{suffix}", delta, up)


def metric_card_group(metrics: List[Dict[str, Any]]):
    """Render a row of neo-brutalist metric cards."""
    if not metrics:
        return
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        delta = m.get('delta')
        up = not (delta and str(delta).startswith('-'))
        _nb_card(col, m.get('title', ''), m.get('value', ''),
                 delta, up, m.get('subtitle'))


def kpi_card(title, value, format_type='number', delta=None,
             target=None, variant='primary'):
    """Neo-brutalist KPI card (compat shim for kpi_card)."""
    try:
        if format_type == 'currency':
            fval = format_currency(value)
        elif format_type == 'percentage':
            fval = format_percentage(float(value))
        else:
            fval = format_number(int(float(value)))
    except Exception:
        fval = str(value)

    d_str = None
    up = True
    if delta is not None:
        sign = '+' if float(delta) >= 0 else ''
        d_str = f"{sign}{float(delta):.1f}%"
        up = float(delta) >= 0

    sub = None
    if target is not None and target > 0:
        try:
            pct = min((float(value) / target) * 100, 100)
            sub = f"Target: {pct:.0f}% of {target}"
        except Exception:
            pass

    _nb_card(st, title, fval, d_str, up, sub)
