import streamlit as st
import pandas as pd
from contextlib import contextmanager
from typing import Any, List, Optional


# ── Color & style maps ──────────────────────────────────

_VARIANT_STYLES = {
    "primary": {
        "bg":     "rgba(16, 185, 129, 0.12)",
        "border": "#10b981",
        "icon":   "ℹ️",
    },
    "success": {
        "bg":     "rgba(0, 214, 143, 0.12)",
        "border": "#00d68f",
        "icon":   "✅",
    },
    "warning": {
        "bg":     "rgba(255, 171, 0, 0.12)",
        "border": "#ffab00",
        "icon":   "⚠️",
    },
    "danger": {
        "bg":     "rgba(255, 82, 82, 0.12)",
        "border": "#ff5252",
        "icon":   "🚨",
    },
    "info": {
        "bg":     "rgba(16, 185, 129, 0.08)",
        "border": "#718096",
        "icon":   "💡",
    },
    "default": {
        "bg":     "rgba(255, 255, 255, 0.05)",
        "border": "#4a5568",
        "icon":   "▪️",
    },
}

_BADGE_COLORS = {
    "success": ("#00d68f", "#0a2e1f"),
    "warning": ("#ffab00", "#2e2200"),
    "danger":  ("#ff5252", "#2e0a0a"),
    "primary": ("#10b981", "#062018"),
    "info":    ("#718096", "#1a1e26"),
    "default": ("#a0aec0", "#1a1e26"),
}

_BAR_COLORS = {
    "primary": "#10b981",
    "success": "#00d68f",
    "warning": "#ffab00",
    "danger":  "#ff5252",
    "info":    "#718096",
}


# ── Alert boxes ─────────────────────────────────────────

def alert_box(message: str, variant: str = "info") -> None:
    """
    Display a styled alert banner.

    Args:
        message: Text to display (supports markdown/emoji)
        variant: "info" | "warning" | "danger" | "success" | "primary" | "default"

    Example:
        alert_box("⚠️ Backend unavailable. Showing demo data.", "warning")
    """
    style = _VARIANT_STYLES.get(variant, _VARIANT_STYLES["info"])
    st.markdown(
        f"""
        <div style="background: {style['bg']}; border-left: 4px solid {style['border']}; padding: 0.85rem 1.1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0 1rem 0; font-size: 0.9rem; line-height: 1.5;">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def success_box(message: str) -> None:
    """Green success banner. Shorthand for alert_box(msg, 'success')."""
    alert_box(message, "success")


def error_box(message: str) -> None:
    """Red error banner. Shorthand for alert_box(msg, 'danger')."""
    alert_box(message, "danger")


def warning_box(message: str) -> None:
    """Yellow warning banner. Shorthand for alert_box(msg, 'warning')."""
    alert_box(message, "warning")


# ── Stat card ────────────────────────────────────────────

def stat_card(
    label: str,
    value: Any,
    icon: str = "📊",
    delta: Optional[str] = None,
    delta_positive: bool = True,
    variant: str = "primary",
    help_text: Optional[str] = None,
) -> None:
    """Neo-brutalist stat card."""
    D   = st.session_state.get('theme', 'dark') == 'dark'
    BG  = '#141414' if D else '#ffffff'
    BOR = '#262626'  if D else '#0a0a0a'
    T   = '#f5f5f5' if D else '#0a0a0a'
    T2  = '#a3a3a3' if D else '#737373'
    SHD = '2px 2px 0px rgba(255,255,255,0.08)' if D else '4px 4px 0px #0a0a0a'
    dc  = '#10b981' if delta_positive else '#ef4444'
    d_html = f'<div style="font-size:.75rem;color:{dc};margin-top:.35rem;font-weight:600;">{delta}</div>' if delta else ''
    st.markdown(f'''<div style="background:{BG};border:2px solid {BOR};border-radius:0;
padding:1rem 1.1rem .9rem;position:relative;overflow:hidden;box-shadow:{SHD};">
<div style="position:absolute;top:0;left:0;right:0;height:3px;background:#10b981;"></div>
<div style="font-size:1.4rem;margin-bottom:.3rem;">{icon}</div>
<div style="font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:{T};line-height:1.2;">{value}</div>
<div style="font-family:JetBrains Mono,monospace;font-size:.6rem;color:{T2};text-transform:uppercase;letter-spacing:.1em;margin-top:.2rem;">{label}</div>
{d_html}
</div>''', unsafe_allow_html=True)


# ── Animated progress bar ────────────────────────────────

def progress_bar_animated(
    value: float,
    max_value: float = 100,
    show_percentage: bool = True,
    color: str = "primary",
    height: int = 8,
    label: Optional[str] = None,
) -> None:
    """
    CSS-animated horizontal progress bar.

    Args:
        value:          Current value
        max_value:      Maximum value (bar fills to value/max_value)
        show_percentage: Show percentage text on the right
        color:          "primary" | "success" | "warning" | "danger" | "info"
        height:         Bar height in pixels
        label:          Optional label above the bar

    Example:
        progress_bar_animated(agent['success_rate'], 100, show_percentage=True, color='success')
    """
    pct     = min((value / max_value) * 100, 100) if max_value > 0 else 0
    bar_clr = _BAR_COLORS.get(color, _BAR_COLORS["primary"])

    label_html = (
        f'<div style="font-size:0.8rem; opacity:0.75; margin-bottom:0.2rem;">{label}</div>'
        if label else ""
    )
    pct_html = (
        f'<span style="font-size:0.8rem; font-weight:700; color:{bar_clr}; ' f'min-width:3rem; text-align:right;">{pct:.1f}%</span>'
        if show_percentage else ""
    )

    st.markdown(
        f"""
        {label_html}
        <div style="display:flex; align-items:center; gap:0.6rem; margin:0.2rem 0;">
            <div style="flex:1; background: rgba(255,255,255,0.1); border-radius: {height}px; height: {height}px; overflow: hidden;">
                <div style="background: {bar_clr}; height: 100%; width: {pct}%; border-radius: {height}px; transition: width 0.6s cubic-bezier(0.4,0,0.2,1);"></div>
            </div>
            {pct_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Card container ───────────────────────────────────────

@contextmanager
def card_container(
    title: str,
    icon: str = "▪️",
    variant: str = "default",
    padding: str = "1rem 1.25rem",
):
    """Neo-brutalist card container (context manager)."""
    D   = st.session_state.get('theme', 'dark') == 'dark'
    BG  = '#141414' if D else '#ffffff'
    BOR = '#262626'  if D else '#0a0a0a'
    T   = '#f5f5f5' if D else '#0a0a0a'
    SHD = '2px 2px 0px rgba(255,255,255,0.06)' if D else '4px 4px 0px #0a0a0a'
    # Accent line color by variant
    ACC_MAP = {'primary':'#10b981','success':'#10b981','warning':'#f59e0b',
               'danger':'#ef4444','info':'#a3a3a3','default':'#737373'}
    ACC = ACC_MAP.get(variant, '#10b981')

    st.markdown(f'''<div style="background:{BG};border:2px solid {BOR};border-radius:0;
padding:{padding};margin-bottom:1rem;position:relative;overflow:hidden;box-shadow:{SHD};">
<div style="position:absolute;top:0;left:0;right:0;height:3px;background:{ACC};"></div>
<div style="font-family:Syne,sans-serif;font-size:.9rem;font-weight:700;color:{T};
  margin-bottom:.75rem;display:flex;align-items:center;gap:.45rem;">
  <span>{icon}</span><span>{title}</span></div>
''', unsafe_allow_html=True)

    yield

    st.markdown("</div>", unsafe_allow_html=True)


# ── Status badge ─────────────────────────────────────────

def status_badge(label: str, variant: str = "default") -> None:
    """
    Inline colored pill badge.

    Args:
        label:   Text inside the badge
        variant: "success" | "warning" | "danger" | "primary" | "info" | "default"

    Example:
        status_badge("Low Risk", "success")
        status_badge("CRITICAL", "danger")
    """
    fg, bg = _BADGE_COLORS.get(variant, _BADGE_COLORS["default"])
    st.markdown(
        f"""
        <span style="background: {bg}; color: {fg}; border: 1px solid {fg}66; border-radius: 20px; padding: 0.2rem 0.7rem; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.03em; display: inline-block;">{label}</span>
        """,
        unsafe_allow_html=True,
    )


# ── Data table ───────────────────────────────────────────

def data_table(
    data: List[dict],
    columns: Optional[List[str]] = None,
    max_height: int = 400,
    hide_index: bool = True,
    use_container_width: bool = True,
) -> None:
    """
    Styled DataFrame display with optional column selection.

    Args:
        data:                  List of dicts (rows)
        columns:               Column keys to display (None = all columns)
        max_height:            Max scrollable height in pixels
        hide_index:            Hide DataFrame index
        use_container_width:   Stretch to full container width

    Example:
        data_table(
            data=industries,
            columns=['name', 'count', 'amount'],
            max_height=300
        )
    """
    if not data:
        st.info("No data to display.")
        return

    df = pd.DataFrame(data)

    if columns:
        # Keep only requested columns that actually exist
        valid_cols = [c for c in columns if c in df.columns]
        if valid_cols:
            df = df[valid_cols]

    st.dataframe(
        df,
        use_container_width=use_container_width,
        hide_index=hide_index,
        height=min(max_height, (len(df) + 1) * 35 + 10),  # auto-fit short tables
    )


# ── Empty state ──────────────────────────────────────────

def empty_state(
    message: str,
    icon: str = "📭",
    action_text: Optional[str] = None,
    action_callback=None,
) -> None:
    """
    Centered empty-state placeholder with optional action button.

    Args:
        message:         Main message text
        icon:            Large emoji shown above message
        action_text:     Label for the action button (None = no button)
        action_callback: Callable triggered when button is clicked

    Example:
        empty_state(
            message="No active fraud scenarios detected",
            icon="✅",
            action_text="Refresh",
            action_callback=lambda: st.rerun()
        )
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 1rem; opacity: 0.7;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <div style="font-size: 1rem; color: #a0aec0;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if action_text and action_callback:
        col = st.columns([1, 2, 1])[1]
        with col:
            if st.button(action_text, use_container_width=True):
                action_callback()


# ── Timeline item ────────────────────────────────────────

def timeline_item(
    title: str,
    description: str = "",
    timestamp: str = "",
    status: str = "info",
) -> None:
    """
    Single item in a vertical timeline list.

    Args:
        title:       Bold title text
        description: Secondary description text
        timestamp:   Time string shown on the right
        status:      "info" | "success" | "warning" | "error"

    Example:
        timeline_item(
            title=event['title'],
            description=event['description'],
            timestamp=event['timestamp'],
            status='error' if event['severity'] in ['CRITICAL', 'HIGH'] else 'warning'
        )
    """
    _status_map = {
        "info":    ("#4A9EFF", "ℹ️"),
        "success": ("#00d68f", "✅"),
        "warning": ("#ffab00", "⚠️"),
        "error":   ("#ff5252", "🔴"),
    }
    color, dot_icon = _status_map.get(status, _status_map["info"])

    st.markdown(
        f"""
        <div style="display: flex; gap: 1rem; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.06); align-items: flex-start;">
            <div style="font-size: 1.1rem; margin-top: 0.1rem; flex-shrink: 0;">{dot_icon}</div>
            <div style="flex: 1; min-width: 0;">
                <div style="font-weight: 700; font-size: 0.9rem; color: {color};">{title}</div>
                {f'<div style="font-size:0.8rem; opacity:0.65; margin-top:0.2rem;">{description}</div>' if description else ''}
            </div>
            {f'<div style="font-size:0.75rem; opacity:0.5; flex-shrink:0; padding-top:0.1rem;">{timestamp}</div>' if timestamp else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_box(message: str) -> None:
    """Blue info banner. Shorthand for alert_box(msg, 'info')."""
    alert_box(message, "info")


def info_tooltip(text: str, icon: str = "ℹ️") -> None:
    """Inline icon with hover tooltip text."""
    st.markdown(
        f'<span title="{text}" style="cursor:help;font-size:1rem;">{icon}</span>',
        unsafe_allow_html=True
    )


def loading_spinner(message: str = "Loading...") -> None:
    """Animated loading indicator."""
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.75rem;padding:1rem;opacity:0.7;">'
        f'<div style="width:20px;height:20px;border:3px solid rgba(74,158,255,0.3);' f'border-top-color:#4A9EFF;border-radius:50%;animation:spin 0.8s linear infinite;"></div>'
        f'<span style="font-size:0.9rem;">{message}</span>'
        f'</div>',
        unsafe_allow_html=True
    )