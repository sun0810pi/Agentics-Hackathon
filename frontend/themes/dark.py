DARK_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #060912;
    --bg2:      #0c1020;
    --bg3:      #111827;
    --bg4:      #1e2a3a;
    --primary:  #3b82f6;
    --cyan:     #06b6d4;
    --green:    #10b981;
    --yellow:   #f59e0b;
    --red:      #ef4444;
    --purple:   #8b5cf6;
    --text:     #f1f5f9;
    --text2:    #94a3b8;
    --text3:    #475569;
    --border:   rgba(59,130,246,0.12);
    --border2:  rgba(59,130,246,0.25);
    --card:     rgba(12,16,32,0.8);
    --glow:     0 0 20px rgba(59,130,246,0.15);
    --radius:   12px;
    --gap:      1.25rem;
}

/* ── Reset & Base ───────────────────────────────────────────── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarNav"],
[data-testid="stStatusWidget"] { display: none !important; }

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── App background with depth ─────────────────────────────── */
.stApp > [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 10% -10%, rgba(59,130,246,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 110%, rgba(6,182,212,0.06) 0%, transparent 55%),
        radial-gradient(ellipse 40% 30% at 50% 50%, rgba(139,92,246,0.03) 0%, transparent 50%),
        #060912 !important;
}

/* ── Layout: zero padding ───────────────────────────────────── */
.stApp > [data-testid="stAppViewContainer"] > section.main { padding: 0 !important; }
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    margin: 0 !important;
}

/* ── Columns: flush full height ─────────────────────────────── */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    align-items: stretch !important;
}
[data-testid="stHorizontalBlock"] > div {
    padding: 0 !important;
    margin: 0 !important;
}

/* ── Sidebar (first column) ─────────────────────────────────── */
[data-testid="column"]:first-of-type {
    background: linear-gradient(180deg, #0a0e1a 0%, #070b14 100%) !important;
    border-right: 1px solid var(--border2) !important;
    min-height: 100vh !important;
    position: sticky !important;
    top: 0 !important;
    overflow-y: auto !important;
    max-height: 100vh !important;
}

/* ── Content (second column) ────────────────────────────────── */
[data-testid="column"]:last-of-type {
    background: var(--bg) !important;
    min-height: 100vh !important;
    overflow-y: auto !important;
}

/* ── Typography ──────────────────────────────────────────────── */
h1 { font-size: 1.75rem !important; font-weight: 700 !important; color: var(--text) !important; letter-spacing: -0.025em !important; line-height: 1.2 !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: var(--text) !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: var(--text) !important; }
h4 { font-size: 0.9rem !important; font-weight: 600 !important; color: var(--text2) !important; text-transform: uppercase; letter-spacing: 0.06em; }
p, span, div, li { color: var(--text) !important; line-height: 1.6; }
label { color: var(--text2) !important; font-size: 0.78rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.06em; }
code { font-family: 'JetBrains Mono', monospace !important; font-size: 0.85em; }

/* ── Buttons ─────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    background: var(--bg3) !important;
    color: var(--text2) !important;
    transition: all 0.15s ease !important;
    padding: 0.5rem 1rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    border-color: var(--border2) !important;
    color: var(--text) !important;
    background: var(--bg4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, #2563eb 100%) !important;
    border: 1px solid rgba(59,130,246,0.4) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4f92ff 0%, #3b82f6 100%) !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.45) !important;
    transform: translateY(-1px) !important;
    color: #fff !important;
}

/* ── Inputs ──────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    outline: none !important;
}
.stSelectbox > div > div { border-radius: 8px !important; }

/* ── Metrics ─────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.25rem 1.5rem !important;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border2) !important;
    box-shadow: var(--glow) !important;
}
[data-testid="stMetric"]::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--cyan));
    opacity: 0.6;
}
[data-testid="stMetricLabel"] { margin-bottom: 0.4rem; }
[data-testid="stMetricLabel"] > div {
    color: var(--text2) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] > div { font-size: 0.8rem !important; margin-top: 0.35rem; }

/* ── Divider ─────────────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Expander ────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 0.75rem !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; font-weight: 500 !important; padding: 0.875rem 1rem !important; }
[data-testid="stExpander"] > div > div { padding: 0 1rem 1rem !important; }

/* ── Tabs ────────────────────────────────────────────────────── */
[data-testid="stTabs"] { border-bottom: 1px solid var(--border) !important; }
[data-testid="stTabs"] button {
    color: var(--text2) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.15s !important;
}
[data-testid="stTabs"] button:hover { color: var(--text) !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom-color: var(--primary) !important;
    font-weight: 600 !important;
}

/* ── Alerts ──────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: var(--radius) !important; border-width: 1px !important; }
[data-testid="stAlert"][data-baseweb="notification"] { padding: 0.875rem 1rem !important; }

/* ── Dataframe ───────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: var(--radius) !important; overflow: hidden !important; }
[data-testid="stDataFrame"] table { font-size: 0.875rem !important; }
[data-testid="stDataFrame"] th { background: var(--bg3) !important; color: var(--text2) !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stDataFrame"] td { color: var(--text) !important; border-color: var(--border) !important; }

/* ── File uploader ───────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg2) !important;
    transition: border-color 0.2s !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--primary) !important; }

/* ── Slider ──────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--cyan)) !important;
}

/* ── Progress ────────────────────────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--cyan)) !important;
    border-radius: 99px !important;
}
.stProgress > div > div {
    background: var(--bg3) !important;
    border-radius: 99px !important;
}

/* ── Selectbox dropdown ──────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* ── Info/Success/Warning/Error boxes ────────────────────────── */
.stAlert { border-left-width: 3px !important; }

/* ── Spinner ─────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ── Checkbox / Radio ────────────────────────────────────────── */
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label { color: var(--text) !important; font-size: 0.9rem !important; }

/* ── Scrollbar ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.25); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── Caption ─────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] { color: var(--text2) !important; font-size: 0.8rem !important; }

/* ── Status badge helper ─────────────────────────────────────── */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 10px; border-radius: 99px;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
}
.badge-green { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.2); }
.badge-red { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }
.badge-yellow { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
.badge-blue { background: rgba(59,130,246,0.12); color: #3b82f6; border: 1px solid rgba(59,130,246,0.2); }

/* ── Responsive: mobile ──────────────────────────────────────── */
@media (max-width: 768px) {
    [data-testid="column"]:first-of-type {
        position: relative !important;
        max-height: none !important;
        min-height: auto !important;
        border-right: none !important;
        border-bottom: 1px solid var(--border2) !important;
    }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    h1 { font-size: 1.4rem !important; }
}
</style>
"""
