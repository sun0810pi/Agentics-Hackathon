DARK_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg:      #060912;
    --bg2:     #0c1020;
    --bg3:     #111827;
    --bg4:     #1a2235;
    --primary: #3b82f6;
    --cyan:    #06b6d4;
    --green:   #10b981;
    --yellow:  #f59e0b;
    --red:     #ef4444;
    --text:    #e2e8f0;
    --text2:   #94a3b8;
    --text3:   #4b5563;
    --border:  rgba(59,130,246,0.15);
    --glow:    rgba(59,130,246,0.4);
}

#MainMenu,footer,[data-testid="stToolbar"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}

/* App background */
.stApp {
    background: var(--bg);
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text);
}
.stApp > [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #060912 0%, #0a0f1e 50%, #060912 100%);
}

/* Scanline overlay */
.stApp::before {
    content:'';
    position:fixed;
    inset:0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
    pointer-events:none;
    z-index:0;
}

/* Main container */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1280px;
    position: relative;
    z-index: 1;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1020 0%, #070b16 100%) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 4px 0 30px rgba(0,0,0,0.5) !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}

/* Sidebar toggle — native button */
[data-testid="collapsedControl"] {
    display:flex !important;
    visibility:visible !important;
    opacity:1 !important;
}

/* Typography */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.85rem !important;
    color: var(--text) !important;
    letter-spacing: -0.02em;
}
h2,h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}
p,span,div,li,label { color: var(--text) !important; }
label { color: var(--text2) !important; font-size: 0.82rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.05em; }

/* Buttons */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    background: var(--bg3) !important;
    color: var(--text2) !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    border-color: var(--primary) !important;
    color: var(--text) !important;
    background: rgba(59,130,246,0.08) !important;
    box-shadow: 0 0 12px rgba(59,130,246,0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.5) !important;
    color: #fff !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15), 0 0 20px rgba(59,130,246,0.1) !important;
    outline: none !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content:'';
    position:absolute;
    top:0; left:0; right:0;
    height:2px;
    background: linear-gradient(90deg, var(--primary), var(--cyan));
    opacity: 0.7;
}
[data-testid="stMetricLabel"] > div {
    color: var(--text2) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* Divider */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Tabs */
[data-testid="stTabs"] {
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTabs"] button {
    color: var(--text2) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* Alerts */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* Tables */
table { border-collapse: collapse !important; width: 100%; font-family: 'Space Grotesk', sans-serif; }
th { background: var(--bg3) !important; color: var(--text2) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; padding: 0.65rem 1rem; border-bottom: 1px solid var(--border) !important; }
td { border-bottom: 1px solid var(--border) !important; padding: 0.65rem 1rem; color: var(--text) !important; }
tr:hover td { background: rgba(59,130,246,0.04) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg3) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
}

/* Slider */
[data-testid="stSlider"] > div > div > div > div { background: var(--primary) !important; }

/* Checkbox / Radio */
[data-testid="stCheckbox"] span, [data-testid="stRadio"] label { color: var(--text) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* Progress */
.stProgress > div > div > div { background: linear-gradient(90deg, var(--primary), var(--cyan)) !important; }

/* Code */
code, .stCode { font-family: 'JetBrains Mono', monospace !important; background: var(--bg3) !important; color: var(--cyan) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* Warning box */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(245,158,11,0.1) !important;
    border-color: var(--yellow) !important;
}

/* ── Force sidebar always open ──────────────────────────── */
/* Hide the collapse button inside sidebar (prevents closing) */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[aria-label="Close sidebar"] { display: none !important; }
/* Make sure sidebar toggle in header is visible for opening */
[data-testid="stMainMenuPopover"] button { display: none !important; }
</style>
"""
