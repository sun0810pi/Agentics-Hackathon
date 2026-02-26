LIGHT_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg:      #f0f4ff;
    --bg2:     #ffffff;
    --bg3:     #f8faff;
    --bg4:     #eef2ff;
    --primary: #2563eb;
    --cyan:    #0891b2;
    --green:   #059669;
    --yellow:  #d97706;
    --red:     #dc2626;
    --text:    #0f172a;
    --text2:   #475569;
    --text3:   #94a3b8;
    --border:  rgba(37,99,235,0.12);
    --glow:    rgba(37,99,235,0.3);
}

#MainMenu,footer,[data-testid="stToolbar"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}

.stApp {
    background: var(--bg) !important;
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text);
}

[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;}

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 4px 0 20px rgba(37,99,235,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child { background: var(--bg2) !important; }

.main .block-container { padding: 2rem 2.5rem !important; max-width: 1280px; }

h1 { font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important; font-size: 1.85rem !important; color: var(--text) !important; letter-spacing: -0.02em; }
h2,h3 { font-family: 'Space Grotesk', sans-serif !important; font-weight: 600 !important; color: var(--text) !important; }
p,span,div,li { color: var(--text) !important; }
label { color: var(--text2) !important; font-size: 0.82rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.05em; }

.stButton > button {
    border-radius: 8px !important; border: 1px solid var(--border) !important;
    background: var(--bg2) !important; color: var(--text2) !important;
    font-family: 'Space Grotesk', sans-serif !important; font-weight: 500 !important;
    transition: all 0.18s !important; box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
.stButton > button:hover { border-color: var(--primary) !important; color: var(--primary) !important; background: rgba(37,99,235,0.04) !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary), var(--cyan)) !important;
    border: none !important; color: #fff !important; font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 18px rgba(37,99,235,0.4) !important; color: #fff !important; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: var(--bg2) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
.stTextInput > div > div > input:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important; }

[data-testid="stSelectbox"] > div > div { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text) !important; }

[data-testid="stMetric"] {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; padding: 1.25rem !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.06) !important; position: relative; overflow: hidden;
}
[data-testid="stMetric"]::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; background: linear-gradient(90deg, var(--primary), var(--cyan)); }
[data-testid="stMetricLabel"] > div { color: var(--text2) !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'Space Grotesk' !important; font-size: 1.9rem !important; font-weight: 700 !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }
[data-testid="stExpander"] { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important; }
[data-testid="stTabs"] button { color: var(--text2) !important; font-family: 'Space Grotesk', sans-serif !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color: var(--primary) !important; border-bottom: 2px solid var(--primary) !important; }
table { border-collapse: collapse !important; width: 100%; }
th { background: var(--bg3) !important; color: var(--text2) !important; font-size: 0.75rem !important; text-transform: uppercase; padding: 0.65rem 1rem; border-bottom: 1px solid var(--border) !important; }
td { border-bottom: 1px solid var(--border) !important; padding: 0.65rem 1rem; color: var(--text) !important; }
tr:hover td { background: rgba(37,99,235,0.03) !important; }
[data-testid="stFileUploader"] { border: 2px dashed var(--border) !important; border-radius: 12px !important; background: var(--bg3) !important; }
[data-testid="stSlider"] > div > div > div > div { background: var(--primary) !important; }
[data-testid="stCheckbox"] span,[data-testid="stRadio"] label { color: var(--text) !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--primary), var(--cyan)) !important; }
code,.stCode { font-family: 'JetBrains Mono',monospace !important; background: var(--bg4) !important; color: var(--primary) !important; }
::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: var(--bg3); } ::-webkit-scrollbar-thumb { background: rgba(37,99,235,0.2); border-radius: 3px; }

/* ── Force sidebar always open ──────────────────────────── */
/* Hide the collapse button inside sidebar (prevents closing) */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[aria-label="Close sidebar"] { display: none !important; }
/* Make sure sidebar toggle in header is visible for opening */
[data-testid="stMainMenuPopover"] button { display: none !important; }
</style>
"""
