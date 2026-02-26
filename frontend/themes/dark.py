DARK_THEME = """
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

</style>


/* =====================================================
   🎨 COMPREHENSIVE UI/UX IMPROVEMENTS
   Added for beautiful, spacious, professional design
   ===================================================== */

/* ─── ANIMATED GRADIENT BACKGROUND ─────────────────── */
.main {
    background: linear-gradient(
        135deg,
        #0a0e1a 0%,
        #0f172a 15%,
        #1e1b4b 35%,
        #0f172a 55%,
        #1a1f2e 75%,
        #0f172a 100%
    ) !important;
    background-size: 400% 400% !important;
    animation: gradient-shift 20s ease infinite !important;
}

@keyframes gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Animated mesh overlay */
.main::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(16, 185, 129, 0.06) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 10% 80%, rgba(59, 130, 246, 0.04) 0%, transparent 35%);
    pointer-events: none;
    z-index: 0;
    animation: mesh-float 30s ease-in-out infinite;
}

@keyframes mesh-float {
    0%, 100% { transform: translate(0, 0); }
    33% { transform: translate(30px, -30px); }
    66% { transform: translate(-20px, 20px); }
}

/* ─── GENEROUS SPACING ─────────────────────────────── */

/* Main container - WIDE and SPACIOUS */
.block-container {
    padding: 3rem 5rem 4rem 5rem !important;
    max-width: 1800px !important;
    margin: 0 auto !important;
}

/* Section spacing */
section {
    margin-bottom: 3rem !important;
}

.element-container {
    margin-bottom: 1.5rem !important;
}

/* Column spacing */
[data-testid="column"] {
    padding: 0 1rem !important;
}

[data-testid="column"]:first-child {
    padding-left: 0 !important;
}

[data-testid="column"]:last-child {
    padding-right: 0 !important;
}

/* Divider spacing */
hr {
    margin: 3rem 0 !important;
    opacity: 0.2 !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
}

/* ─── BEAUTIFUL METRIC CARDS ────────────────────────── */
[data-testid="stMetric"],
[data-testid="metric-container"] {
    background: linear-gradient(
        135deg,
        rgba(30, 41, 59, 0.6) 0%,
        rgba(30, 41, 59, 0.4) 100%
    ) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    border-radius: 20px !important;
    padding: 2rem 1.5rem !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

/* Shine effect on hover */
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
        rgba(255, 255, 255, 0.05) 50%,
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
    border-color: rgba(59, 130, 246, 0.5) !important;
    box-shadow: 
        0 16px 48px rgba(0, 0, 0, 0.4),
        0 0 60px rgba(59, 130, 246, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

/* Metric labels */
[data-testid="stMetric"] label,
[data-testid="metric-container"] label {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: rgba(148, 163, 184, 0.9) !important;
    font-weight: 600 !important;
    margin-bottom: 0.75rem !important;
}

/* Metric values */
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #3b82f6, #06b6d4) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

/* Metric delta */
[data-testid="stMetric"] [data-testid="stMetricDelta"],
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 0.25rem 0.5rem !important;
    border-radius: 6px !important;
    background: rgba(16, 185, 129, 0.15) !important;
}

/* ─── CHART CONTAINERS ─────────────────────────────── */
.element-container:has(iframe),
.element-container:has([data-testid="stPlotlyChart"]) {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(59, 130, 246, 0.15) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
}

/* ─── HEADINGS & TEXT ──────────────────────────────── */
h1, h2, h3 {
    margin-top: 2rem !important;
    margin-bottom: 1.5rem !important;
}

h1 {
    font-size: 2.5rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #3b82f6, #06b6d4) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.02em !important;
}

h2 {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: #e2e8f0 !important;
}

h3 {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #cbd5e1 !important;
}

/* Caption/subtitle */
.caption,
[data-testid="stCaption"] {
    color: #94a3b8 !important;
    font-size: 0.95rem !important;
    margin-bottom: 2rem !important;
}

/* ─── SIDEBAR IMPROVEMENTS ─────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        rgba(15, 23, 42, 0.95) 0%,
        rgba(30, 41, 59, 0.95) 100%
    ) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(59, 130, 246, 0.1) !important;
    padding: 1.5rem 1rem !important;
}

/* Sidebar content spacing */
[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* User info card */
[data-testid="stSidebar"] > div > div:first-child {
    margin-bottom: 2rem !important;
}

/* Navigation buttons */
[data-testid="stSidebar"] button {
    margin: 0.5rem 0 !important;
    padding: 0.75rem 1rem !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stSidebar"] button:hover {
    transform: translateX(4px) !important;
}

/* Theme toggle section - push to bottom */
[data-testid="stSidebar"] .row-widget.stButton {
    margin-top: auto !important;
    padding-top: 2rem !important;
}

/* ─── BUTTONS ───────────────────────────────────────── */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25) !important;
}

button:active {
    transform: translateY(0) !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    border: none !important;
    box-shadow: 
        0 4px 12px rgba(59, 130, 246, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

button[kind="primary"]:hover {
    box-shadow: 
        0 8px 24px rgba(59, 130, 246, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
}

/* ─── TABLES ────────────────────────────────────────── */
table {
    border-collapse: separate !important;
    border-spacing: 0 0.5rem !important;
}

thead th {
    background: rgba(30, 41, 59, 0.6) !important;
    padding: 1rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    border: none !important;
}

tbody td {
    background: rgba(30, 41, 59, 0.3) !important;
    padding: 1rem !important;
    border: none !important;
}

tbody tr {
    transition: all 0.2s ease !important;
}

tbody tr:hover {
    background: rgba(59, 130, 246, 0.05) !important;
    transform: scale(1.01) !important;
}

/* ─── ALERTS ────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 16px !important;
    padding: 1.5rem !important;
    border-width: 1px !important;
    backdrop-filter: blur(10px) !important;
    margin: 1.5rem 0 !important;
}

/* ─── LOADING & ANIMATIONS ─────────────────────────── */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.stSpinner > div {
    border-color: #3b82f6 transparent transparent transparent !important;
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
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
}

/* ─── FIXES FOR SPECIFIC ISSUES ────────────────────── */

/* Ensure full width usage */
.main .block-container > div {
    width: 100% !important;
}

/* Remove default Streamlit padding conflicts */
.main .block-container .element-container {
    width: 100% !important;
}

/* Chart full width */
[data-testid="stPlotlyChart"] {
    width: 100% !important;
}

/* Column gap */
.row-widget {
    gap: 2rem !important;
}

</style>

"""