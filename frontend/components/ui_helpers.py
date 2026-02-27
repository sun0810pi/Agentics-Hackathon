"""
Shared UI helpers — Neo-brutalist design system for AgentFlow.
Green accent (#10b981), Syne + DM Sans fonts, bold borders + shadows.
"""
import streamlit as st


def is_dark():
    return st.session_state.get('theme', 'dark') == 'dark'


def _colors(dark=None):
    D = is_dark() if dark is None else dark
    return {
        "acc":   "#10b981",
        "acc2":  "#059669",
        "acc3":  "#34d399",
        "text":  "#f5f5f5" if D else "#0a0a0a",
        "text2": "#a3a3a3" if D else "#737373",
        "text3": "#737373" if D else "#a3a3a3",
        "bg":    "#0a0a0a" if D else "#f5f0eb",
        "bg2":   "#141414" if D else "#ffffff",
        "bg3":   "#1f1f1f" if D else "#f7f4f0",
        "bor":   "#262626" if D else "#e5e0da",
        "bor2":  "rgba(16,185,129,.3)",
    }


def page_header(icon: str, title: str, subtitle: str = None):
    """Large page header with neo-brutalist style."""
    D = is_dark()
    c = _colors(D)
    sub_html = (
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.9rem;'
        f'color:{c["text2"]};margin-top:.35rem;">{subtitle}</div>'
    ) if subtitle else ""
    st.markdown(f"""
<div style="margin-bottom:1.75rem;">
  <div style="display:flex;align-items:center;gap:.6rem;
    font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
    color:{c["text"]};letter-spacing:-.03em;line-height:1.15;">
    <span style="font-size:2rem;">{icon}</span>{title}
  </div>
  {sub_html}
  <div style="height:3px;background:linear-gradient(90deg,{c["acc"]},{c["acc3"]},transparent);
    border-radius:2px;margin-top:.75rem;max-width:200px;"></div>
</div>""", unsafe_allow_html=True)


def section_header(icon: str, title: str, subtitle: str = None):
    """Section-level header."""
    D = is_dark()
    c = _colors(D)
    sub_html = (
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.82rem;'
        f'color:{c["text2"]};margin-top:.2rem;padding-left:1.9rem;">{subtitle}</div>'
    ) if subtitle else ""
    st.markdown(f"""
<div style="margin:2rem 0 .9rem;">
  <div style="display:flex;align-items:center;gap:.4rem;
    font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;
    color:{c["acc"]};text-transform:uppercase;letter-spacing:.04em;">
    <span style="font-size:1.1rem;">{icon}</span>{title}
  </div>
  {sub_html}
</div>""", unsafe_allow_html=True)


def metric_card(col, label: str, value: str, delta: str = None, up: bool = True):
    """Neo-brutalist metric card."""
    D = is_dark()
    c = _colors(D)
    delta_clr = c["acc"] if up else "#ef4444"
    arrow = "↑" if up else "↓"
    delta_html = (
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.78rem;'
        f'color:{delta_clr};margin-top:.4rem;font-weight:600;">{arrow} {delta}</div>'
    ) if delta else ""
    col.markdown(f"""
<div style="background:{c["bg2"]};border:2px solid {c["bor"]};border-radius:12px;
  padding:1rem 1.15rem .9rem;position:relative;overflow:hidden;
  box-shadow:3px 3px 0px {'rgba(0,0,0,0.35)' if D else 'rgba(0,0,0,0.06)'};
  transition:all .2s;">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,{c["acc"]},{c["acc3"]});"></div>
  <div style="font-family:'DM Sans',sans-serif;font-size:.65rem;font-weight:700;
    color:{c["text2"]};text-transform:uppercase;letter-spacing:.12em;
    margin-bottom:.4rem;">{label}</div>
  <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;
    color:{c["text"]};letter-spacing:-.02em;line-height:1.1;">{value}</div>
  {delta_html}
</div>""", unsafe_allow_html=True)


def info_card(title: str, content: str, icon: str = "💡", variant: str = "default"):
    """Info/alert card."""
    D = is_dark()
    c = _colors(D)
    VARIANTS = {
        "success": (c["acc"],  "rgba(16,185,129,.1)", "rgba(16,185,129,.25)"),
        "warning": ("#f59e0b", "rgba(245,158,11,.1)", "rgba(245,158,11,.25)"),
        "error":   ("#ef4444", "rgba(239,68,68,.1)",  "rgba(239,68,68,.25)"),
        "info":    ("#3b82f6", "rgba(59,130,246,.1)",  "rgba(59,130,246,.25)"),
        "default": (c["text2"], c["bg3"],               c["bor"]),
    }
    clr, bg, bor = VARIANTS.get(variant, VARIANTS["default"])
    st.markdown(f"""
<div style="background:{bg};border:2px solid {bor};border-radius:12px;
  padding:1rem 1.15rem;margin:.5rem 0;
  box-shadow:3px 3px 0px {'rgba(0,0,0,0.2)' if D else 'rgba(0,0,0,0.04)'};">
  <div style="display:flex;align-items:center;gap:.5rem;
    font-family:'Syne',sans-serif;font-weight:700;font-size:.9rem;
    color:{clr};margin-bottom:.35rem;">
    {icon} {title}
  </div>
  <div style="font-family:'DM Sans',sans-serif;font-size:.875rem;color:{c["text2"]};
    line-height:1.6;">{content}</div>
</div>""", unsafe_allow_html=True)


def badge(text: str, variant: str = "default"):
    """Inline status badge HTML string."""
    VARIANTS = {
        "success": ("#10b981", "rgba(16,185,129,.12)", "rgba(16,185,129,.3)"),
        "warning": ("#f59e0b", "rgba(245,158,11,.12)", "rgba(245,158,11,.3)"),
        "error":   ("#ef4444", "rgba(239,68,68,.12)",  "rgba(239,68,68,.3)"),
        "info":    ("#3b82f6", "rgba(59,130,246,.12)",  "rgba(59,130,246,.3)"),
        "default": ("#a3a3a3", "rgba(163,163,163,.1)", "rgba(163,163,163,.25)"),
    }
    clr, bg, bor = VARIANTS.get(variant, VARIANTS["default"])
    return (
        f'<span style="display:inline-flex;align-items:center;gap:.3rem;'
        f'background:{bg};border:1.5px solid {bor};border-radius:6px;'
        f'padding:.2rem .65rem;font-family:\'Syne\',sans-serif;font-weight:700;'
        f'font-size:.68rem;color:{clr};text-transform:uppercase;letter-spacing:.06em;">'
        f'<span style="width:5px;height:5px;background:{clr};border-radius:50%;'
        f'display:inline-block;"></span>{text}</span>'
    )


def divider():
    D = is_dark()
    bor = "#262626" if D else "#e5e0da"
    st.markdown(f'<hr style="border:none;border-top:2px solid {bor};margin:1.5rem 0;">', unsafe_allow_html=True)


def spacer(h="1rem"):
    st.markdown(f'<div style="height:{h}"></div>', unsafe_allow_html=True)


def label_tag(text: str):
    D = is_dark()
    c = _colors(D)
    st.markdown(
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:.62rem;font-weight:700;'
        f'color:{c["text2"]};text-transform:uppercase;letter-spacing:.14em;'
        f'margin-bottom:.5rem;">{text}</div>',
        unsafe_allow_html=True
    )
