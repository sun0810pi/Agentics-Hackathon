DARK_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #080c14;
    --bg2:       #0f1420;
    --bg3:       #161c2e;
    --primary:   #3b82f6;
    --primary2:  #60a5fa;
    --accent:    #06b6d4;
    --success:   #10b981;
    --warning:   #f59e0b;
    --danger:    #ef4444;
    --text:      #e2e8f0;
    --text2:     #94a3b8;
    --border:    rgba(59,130,246,0.18);
    --glass:     rgba(15,20,32,0.8);
}

* { box-sizing: border-box; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }

.stApp {
    background: var(--bg);
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: var(--bg2) !important;
}

/* ── Main content padding ─────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1200px;
}

/* ── Typography ──────────────────────────────────────── */
h1 { font-family: 'Syne', sans-serif; font-weight: 800; color: var(--text) !important; font-size: 2rem !important; }
h2, h3 { font-family: 'Syne', sans-serif; font-weight: 700; color: var(--text) !important; }
p, span, div, li { color: var(--text) !important; }

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    background: var(--bg3) !important;
    color: var(--text2) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: var(--primary) !important;
    color: var(--primary2) !important;
    background: rgba(59,130,246,0.1) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    border-color: transparent !important;
    color: white !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    color: white !important;
}

/* ── Inputs ──────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
label { color: var(--text2) !important; font-size: 0.85rem !important; font-weight: 500 !important; }

/* ── Metrics ─────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem !important;
}
[data-testid="stMetricLabel"] > div { color: var(--text2) !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] > div { font-size: 0.82rem !important; }

/* ── Divider ─────────────────────────────────────────── */
hr { border: none; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Expander ────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; }

/* ── Tabs ────────────────────────────────────────────── */
[data-testid="stTabs"] [data-testid="stTab"] {
    color: var(--text2) !important;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    color: var(--primary2) !important;
    border-bottom-color: var(--primary) !important;
}

/* ── Alerts ─────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
}

/* ── Spinner ─────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── Plotly charts dark ──────────────────────────────── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── File uploader ───────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg3) !important;
}

/* ── Selectbox ───────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg3) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* ── Slider ─────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div { background: var(--primary) !important; }

/* ── Checkbox ───────────────────────────────────────── */
[data-testid="stCheckbox"] span { color: var(--text) !important; }

/* ── Radio ──────────────────────────────────────────── */
[data-testid="stRadio"] label { color: var(--text) !important; }

/* ── Status badge helper ─────────────────────────────── */
.status-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;
}

/* ── Markdown tables ─────────────────────────────────── */
table { color: var(--text) !important; border-collapse: collapse; width: 100%; }
th { background: var(--bg3) !important; color: var(--text2) !important; font-size: 0.8rem; text-transform: uppercase; padding: 0.6rem 1rem; }
td { border-bottom: 1px solid var(--border) !important; padding: 0.6rem 1rem; color: var(--text) !important; }

/* ── Password input ──────────────────────────────────── */
input[type="password"] {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
</style>
"""
