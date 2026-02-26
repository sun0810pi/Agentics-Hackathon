LIGHT_THEME = """
<style>

/* ═══ HIDE SIDEBAR COLLAPSE BUTTON - PERMANENT OPEN ══════════════
   The close arrow inside the sidebar - hide every possible selector */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button,
button[data-testid="stSidebarCollapseButton"],
[aria-label="Close sidebar"],
[title="Close sidebar"],
section[data-testid="stSidebar"] button[kind="header"],
.stSidebarCollapseButton,
/* The chevron/arrow icon button in sidebar header */
section[data-testid="stSidebar"] > div > div > div > div > button:first-child {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

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


/* ── App background ─────────────────────────────────────────── */
.stApp > [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 70% 40% at 15% 0%, rgba(37,99,235,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 50% 30% at 85% 100%, rgba(8,145,178,0.04) 0%, transparent 60%),
        #f0f4ff;
}
.login-container { text-align: center; padding: 2rem 0 1rem; }
.login-logo { font-size: 3.5rem; }
.login-title {
    font-size: 1.6rem; font-weight: 700; margin: 0.5rem 0 0.25rem;
    background: linear-gradient(135deg, #2563eb, #0891b2);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.login-subtitle { font-size: 0.78rem; color: #64748b; }

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

</style>


/* =====================================================
   🎨 COMPREHENSIVE UI/UX IMPROVEMENTS - LIGHT THEME
   Professional, spacious, beautiful design
   ===================================================== */

/* ─── ANIMATED GRADIENT BACKGROUND ─────────────────── */
.main {
    background: linear-gradient(
        135deg,
        #f8fafc 0%,
        #f1f5f9 25%,
        #e0e7ff 45%,
        #f1f5f9 65%,
        #fafafa 85%,
        #f8fafc 100%
    ) !important;
    background-size: 400% 400% !important;
    animation: gradient-shift 20s ease infinite !important;
}

@keyframes gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Subtle mesh overlay */
.main::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 30%, rgba(37, 99, 235, 0.04) 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(16, 185, 129, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.02) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* ─── GENEROUS SPACING ─────────────────────────────── */
.block-container {
    padding: 3rem 5rem 4rem 5rem !important;
    max-width: 1800px !important;
    margin: 0 auto !important;
}

section {
    margin-bottom: 3rem !important;
}

.element-container {
    margin-bottom: 1.5rem !important;
}

[data-testid="column"] {
    padding: 0 1rem !important;
}

hr {
    margin: 3rem 0 !important;
    opacity: 0.15 !important;
    border-color: rgba(37, 99, 235, 0.2) !important;
}

/* ─── BEAUTIFUL METRIC CARDS ────────────────────────── */
[data-testid="stMetric"],
[data-testid="metric-container"] {
    background: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.9) 0%,
        rgba(248, 250, 252, 0.9) 100%
    ) !important;
    border: 1px solid rgba(37, 99, 235, 0.15) !important;
    border-radius: 20px !important;
    padding: 2rem 1.5rem !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

[data-testid="stMetric"]::before,
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(37, 99, 235, 0.03) 50%,
        transparent 100%
    );
    transition: left 0.6s ease;
}

[data-testid="stMetric"]:hover::before,
[data-testid="metric-container"]:hover::before {
    left: 100%;
}

[data-testid="stMetric"]:hover,
[data-testid="metric-container"]:hover {
    transform: translateY(-6px) scale(1.02) !important;
    border-color: rgba(37, 99, 235, 0.3) !important;
    box-shadow: 
        0 16px 48px rgba(0, 0, 0, 0.12),
        0 0 40px rgba(37, 99, 235, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 1) !important;
}

[data-testid="stMetric"] label,
[data-testid="metric-container"] label {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #64748b !important;
    font-weight: 600 !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

/* ─── CHART CONTAINERS ─────────────────────────────── */
.element-container:has(iframe),
.element-container:has([data-testid="stPlotlyChart"]) {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(37, 99, 235, 0.12) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 1) !important;
}

/* ─── HEADINGS ─────────────────────────────────────── */
h1 {
    font-size: 2.5rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-top: 2rem !important;
    margin-bottom: 1.5rem !important;
}

h2 {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: #1e293b !important;
    margin-top: 2rem !important;
    margin-bottom: 1.5rem !important;
}

h3 {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #334155 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
}

/* ─── SIDEBAR ───────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        rgba(248, 250, 252, 0.95) 0%,
        rgba(241, 245, 249, 0.95) 100%
    ) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(37, 99, 235, 0.1) !important;
    padding: 1.5rem 1rem !important;
}

[data-testid="stSidebar"] button {
    margin: 0.5rem 0 !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stSidebar"] button:hover {
    transform: translateX(4px) !important;
}

/* ─── BUTTONS ───────────────────────────────────────── */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

button:hover {
    transform: translateY(-2px) !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1e40af) !important;
    border: none !important;
    box-shadow: 
        0 4px 12px rgba(37, 99, 235, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
}

button[kind="primary"]:hover {
    box-shadow: 
        0 8px 24px rgba(37, 99, 235, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}

/* ─── TABLES ────────────────────────────────────────── */
table {
    border-collapse: separate !important;
    border-spacing: 0 0.5rem !important;
}

thead th {
    background: rgba(241, 245, 249, 0.8) !important;
    padding: 1rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
}

tbody td {
    background: rgba(255, 255, 255, 0.6) !important;
    padding: 1rem !important;
}

tbody tr:hover {
    background: rgba(37, 99, 235, 0.03) !important;
}

/* ─── ALERTS ────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 16px !important;
    padding: 1.5rem !important;
    backdrop-filter: blur(10px) !important;
    margin: 1.5rem 0 !important;
}

/* ─── RESPONSIVE ────────────────────────────────────── */
@media (max-width: 1400px) {
    .block-container {
        padding: 2rem 3rem !important;
    }
}

@media (max-width: 1024px) {
    .block-container {
        padding: 1.5rem 2rem !important;
    }
}

/* ─── FULL WIDTH ────────────────────────────────────── */
.main .block-container > div {
    width: 100% !important;
}

.row-widget {
    gap: 2rem !important;
}

</style>

"""