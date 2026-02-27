LIGHT_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #f5f0eb;
  --bg2: #ffffff;
  --bg3: #f7f4f0;
  --bg4: #ede8e2;
  --accent: #10b981;
  --accent2: #059669;
  --accent3: #34d399;
  --blue: #3b82f6;
  --blue2: #2563eb;
  --yellow: #f59e0b;
  --red: #ef4444;
  --text: #0a0a0a;
  --text2: #404040;
  --text3: #737373;
  --border: #e5e0da;
  --border2: rgba(16,185,129,0.35);
  --shadow: 3px 3px 0px rgba(0,0,0,0.08);
  --shadow-accent: 3px 3px 0px rgba(16,185,129,0.25);
  --radius: 12px;
  --font-head: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

/* Kill Streamlit chrome */
#MainMenu,footer,header,
[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],[data-testid="stStatusWidget"],
[data-testid="stSidebar"],[data-testid="collapsedControl"] { display:none!important; }

html,body { margin:0!important; padding:0!important; }
*,*::before,*::after { box-sizing:border-box; }

/* Base */
.stApp {
  font-family: var(--font-body) !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* Subtle grid pattern */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,0,0,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.035) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

/* Layout */
.stApp>[data-testid="stAppViewContainer"] { padding:0!important; margin:0!important; position:relative; z-index:1; }
.stApp>[data-testid="stAppViewContainer"]>section.main,
[data-testid="stMain"],
section[data-testid="stMain"] { padding:0!important; margin:0!important; }
.main,.main .block-container,[data-testid="stMainBlockContainer"],[data-testid="block-container"] {
  padding:0!important; max-width:100%!important; margin:0!important; width:100%!important;
}
section.main>div:first-child,[data-testid="stMain"]>div:first-child { padding:0!important; margin:0!important; }

/* Top-level columns: no gap (nav | content split) */
.block-container>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"],
.main>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"],
section.main [data-testid="stHorizontalBlock"]:first-of-type {
  gap:0!important; padding:0!important; margin:0!important; width:100%!important; align-items:flex-start!important;
}
[data-testid="stHorizontalBlock"] { align-items:flex-start!important; padding:0!important; margin:0!important; width:100%!important; }
[data-testid="column"]:last-of-type [data-testid="stHorizontalBlock"] { gap:0.6rem!important; }
[data-testid="stHorizontalBlock"]>div { padding:0!important; margin:0!important; }

/* Nav column — Neo-brutalist */
[data-testid="column"]:first-of-type {
  background: var(--bg2) !important;
  border-right: 2.5px solid var(--border) !important;
  box-shadow: 3px 0 0px rgba(0,0,0,0.06) !important;
  min-height: 100vh !important;
  position: sticky !important; top: 0 !important;
  overflow-y: auto !important; max-height: 100vh !important;
}
[data-testid="column"]:last-of-type { background: transparent !important; }

/* Typography */
h1 {
  font-family: var(--font-head) !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  color: var(--text) !important;
  letter-spacing: -.03em !important;
  line-height: 1.15 !important;
}
h2 {
  font-family: var(--font-head) !important;
  font-size: 1.4rem !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  letter-spacing: -.02em !important;
}
h3 {
  font-family: var(--font-head) !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  color: var(--text2) !important;
}
p, span, li { color: var(--text2) !important; line-height: 1.7; }
label {
  font-family: var(--font-body) !important;
  color: var(--text2) !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: .07em;
}
[data-testid="stCaptionContainer"] { color: var(--text3) !important; font-size: .8rem !important; }
code {
  font-family: var(--font-mono) !important;
  background: rgba(16,185,129,.08) !important;
  color: var(--accent2) !important;
  border-radius: 5px;
  padding: 2px 7px;
  font-size: .85em;
}

/* Metric cards — Neo-brutalist */
[data-testid="stMetric"] {
  background: var(--bg2) !important;
  border: 2px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1.1rem 1.25rem 1rem !important;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow) !important;
  transition: all .2s ease !important;
}
[data-testid="stMetric"]:hover {
  border-color: var(--accent) !important;
  box-shadow: var(--shadow-accent) !important;
  transform: translate(-1px, -1px) !important;
}
[data-testid="stMetric"]::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), var(--accent3));
}
[data-testid="stMetricLabel"]>div {
  font-family: var(--font-body) !important;
  color: var(--text3) !important;
  font-size: .7rem !important;
  text-transform: uppercase !important;
  letter-spacing: .1em !important;
  font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-head) !important;
  color: var(--text) !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  letter-spacing: -.02em !important;
}
[data-testid="stMetricDelta"]>div { font-size: .8rem !important; margin-top: .3rem; }

/* Buttons */
.stButton>button {
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  font-size: .875rem !important;
  border-radius: 9px !important;
  border: 2px solid var(--border) !important;
  background: var(--bg2) !important;
  color: var(--text2) !important;
  transition: all .15s ease !important;
  box-shadow: 2px 2px 0px rgba(0,0,0,0.06) !important;
}
.stButton>button:hover {
  border-color: var(--accent) !important;
  color: var(--accent2) !important;
  background: rgba(16,185,129,.05) !important;
  transform: translate(-1px, -1px) !important;
  box-shadow: 3px 3px 0px rgba(16,185,129,.15) !important;
}
.stButton>button:active {
  transform: translate(1px, 1px) !important;
  box-shadow: 1px 1px 0px rgba(0,0,0,0.06) !important;
}
.stButton>button[kind="primary"] {
  font-family: var(--font-head) !important;
  font-weight: 700 !important;
  background: var(--accent) !important;
  color: #fff !important;
  border: 2px solid var(--accent2) !important;
  box-shadow: 3px 3px 0px var(--accent2) !important;
}
.stButton>button[kind="primary"]:hover {
  background: var(--accent2) !important;
  border-color: #047857 !important;
  box-shadow: 5px 5px 0px #047857 !important;
  transform: translate(-2px, -2px) !important;
  color: #fff !important;
}

/* Inputs */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input {
  font-family: var(--font-body) !important;
  background: var(--bg2) !important;
  color: var(--text) !important;
  border: 2px solid var(--border) !important;
  border-radius: 9px !important;
  font-size: .9rem !important;
  transition: all .2s ease !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(16,185,129,.1) !important;
}
[data-testid="stSelectbox"]>div>div {
  background: var(--bg2) !important;
  border: 2px solid var(--border) !important;
  border-radius: 9px !important;
  color: var(--text) !important;
}

/* Tabs */
[data-testid="stTabs"] { border-bottom: 2px solid var(--border) !important; }
[data-testid="stTabs"] button {
  font-family: var(--font-body) !important;
  color: var(--text3) !important;
  font-weight: 600 !important;
  padding: .7rem 1.25rem !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  font-family: var(--font-head) !important;
  color: var(--accent) !important;
  border-bottom: 2.5px solid var(--accent) !important;
  font-weight: 700 !important;
}

/* Alerts */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  border-width: 2px !important;
  box-shadow: 3px 3px 0px rgba(0,0,0,0.06) !important;
}

/* DataFrame / Tables */
[data-testid="stDataFrame"] {
  border-radius: var(--radius) !important;
  overflow: hidden !important;
  border: 2px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="stDataFrame"] th {
  font-family: var(--font-head) !important;
  background: var(--bg3) !important;
  color: var(--text2) !important;
  font-size: .72rem !important;
  text-transform: uppercase;
  font-weight: 700 !important;
  letter-spacing: .06em !important;
}
[data-testid="stDataFrame"] td { color: var(--text) !important; }

/* Expander */
[data-testid="stExpander"] {
  background: var(--bg2) !important;
  border: 2px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow) !important;
  margin-bottom: .75rem !important;
}
[data-testid="stExpander"] summary {
  font-family: var(--font-head) !important;
  color: var(--text) !important;
  font-weight: 700 !important;
}

/* Progress */
.stProgress>div>div>div {
  background: linear-gradient(90deg, var(--accent), var(--accent3)) !important;
  border-radius: 99px !important;
}
.stProgress>div>div { background: var(--bg4) !important; border-radius: 99px !important; }

/* File uploader */
[data-testid="stFileUploader"] {
  border: 2.5px dashed rgba(16,185,129,.35) !important;
  border-radius: var(--radius) !important;
  background: rgba(16,185,129,.03) !important;
  padding: 1.5rem !important;
}

/* Checkbox, Radio, Toggle */
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label { color: var(--text) !important; }
[data-testid="stToggle"] label { color: var(--text) !important; font-weight: 600 !important; }

/* Plotly */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }

/* Divider */
hr { border: none !important; border-top: 2px solid var(--border) !important; margin: 1.5rem 0 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(16,185,129,.25); border-radius: 2px; }

/* Mobile */
@media (max-width: 768px) {
  [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
  [data-testid="column"]:first-of-type {
    position: relative !important; max-height: none !important;
    min-height: auto !important; border-right: none !important;
    border-bottom: 2px solid var(--border) !important; overflow-y: visible !important;
  }
  [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
  h1 { font-size: 1.5rem !important; }
}
</style>
"""
