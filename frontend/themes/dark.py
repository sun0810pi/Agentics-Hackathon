DARK_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --black:  #0a0a0a;
  --white:  #ffffff;
  --accent: #10b981;
  --gold:   #f59e0b;
  --g100: #f5f5f5; --g200: #e5e5e5; --g300: #d4d4d4;
  --g400: #a3a3a3; --g500: #737373; --g600: #525252;
  --g700: #404040; --g800: #262626; --g900: #171717;
  /* In dark mode, surfaces flip */
  --bg:    #0a0a0a;
  --bg2:   #141414;
  --bg3:   #1a1a1a;
  --bg4:   #222222;
  --text:  #f5f5f5;
  --text2: #a3a3a3;
  --text3: #737373;
  --bor:   #262626;
  --shadow:    4px 4px 0px rgba(255,255,255,0.08);
  --shadow-sm: 2px 2px 0px rgba(255,255,255,0.06);
  --shadow-acc: 4px 4px 0px rgba(16,185,129,0.25);
  --font-display: 'Syne', system-ui, sans-serif;
  --font-body:    'DM Sans', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
}

/* Kill Streamlit chrome */
#MainMenu,footer,header,
[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],[data-testid="stStatusWidget"],
[data-testid="stSidebar"],[data-testid="collapsedControl"] { display:none!important; }

html,body { margin:0!important; padding:0!important; }
*,*::before,*::after { box-sizing:border-box; }

.stApp { font-family:var(--font-body)!important; background:var(--bg)!important; color:var(--text)!important; }

/* Layout */
.stApp>[data-testid="stAppViewContainer"] { padding:0!important; margin:0!important; }
.stApp>[data-testid="stAppViewContainer"]>section.main,
[data-testid="stMain"],section[data-testid="stMain"] { padding:0!important; margin:0!important; }
.main,.main .block-container,[data-testid="stMainBlockContainer"],[data-testid="block-container"] {
  padding:0!important; max-width:100%!important; margin:0!important; width:100%!important;
}
section.main>div:first-child,[data-testid="stMain"]>div:first-child { padding:0!important; margin:0!important; }

.block-container>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"],
.main>[data-testid="stVerticalBlock"]>[data-testid="stHorizontalBlock"],
section.main [data-testid="stHorizontalBlock"]:first-of-type {
  gap:0!important; padding:0!important; margin:0!important; width:100%!important; align-items:flex-start!important;
}
[data-testid="stHorizontalBlock"] { align-items:flex-start!important; padding:0!important; margin:0!important; width:100%!important; }
[data-testid="column"]:last-of-type [data-testid="stHorizontalBlock"] { gap:0.6rem!important; }
[data-testid="stHorizontalBlock"]>div { padding:0!important; margin:0!important; }

/* Nav column */
[data-testid="column"]:first-of-type {
  background: var(--bg2) !important;
  border-right: 2px solid var(--g800) !important;
  min-height: 100vh !important;
  position: sticky !important; top: 0 !important;
  overflow-y: auto !important; max-height: 100vh !important;
}
[data-testid="column"]:last-of-type { background: var(--bg) !important; }

/* Typography */
h1 { font-family:var(--font-display)!important; font-size:2rem!important; font-weight:800!important; color:var(--text)!important; letter-spacing:-.03em!important; line-height:1.1!important; }
h2 { font-family:var(--font-display)!important; font-size:1.5rem!important; font-weight:700!important; color:var(--text)!important; letter-spacing:-.02em!important; }
h3 { font-family:var(--font-display)!important; font-size:1.1rem!important; font-weight:700!important; color:var(--text2)!important; }
p,span,li { color:var(--text2)!important; line-height:1.7; font-family:var(--font-body)!important; }
label { font-family:var(--font-mono)!important; color:var(--text3)!important; font-size:.75rem!important; font-weight:500!important; text-transform:uppercase; letter-spacing:.08em; }
[data-testid="stCaptionContainer"] { color:var(--text3)!important; font-size:.8rem!important; font-family:var(--font-mono)!important; }
code { font-family:var(--font-mono)!important; background:rgba(16,185,129,.08)!important; color:var(--accent)!important; border:1px solid rgba(16,185,129,.2); padding:2px 7px; font-size:.85em; }

/* Metric cards */
[data-testid="stMetric"] {
  background: var(--bg2) !important;
  border: 2px solid var(--g800) !important;
  border-radius: 0 !important;
  padding: 1.1rem 1.25rem 1rem !important;
  position: relative; overflow: hidden;
  box-shadow: var(--shadow) !important;
  transition: all .15s ease !important;
}
[data-testid="stMetric"]:hover {
  border-color: var(--accent) !important;
  transform: translate(-2px,-2px) !important;
  box-shadow: var(--shadow-acc) !important;
}
[data-testid="stMetric"]::after {
  content:''; position:absolute; top:0; left:0; right:0; height:3px;
  background: var(--accent);
}
[data-testid="stMetricLabel"]>div { font-family:var(--font-mono)!important; color:var(--text3)!important; font-size:.7rem!important; text-transform:uppercase!important; letter-spacing:.1em!important; font-weight:500!important; }
[data-testid="stMetricValue"] { font-family:var(--font-display)!important; color:var(--text)!important; font-size:2.1rem!important; font-weight:800!important; letter-spacing:-.02em!important; }
[data-testid="stMetricDelta"]>div { font-size:.8rem!important; margin-top:.3rem; }

/* Buttons */
.stButton>button {
  font-family:var(--font-body)!important; font-weight:600!important; font-size:.875rem!important;
  border-radius:0!important; border:2px solid var(--g700)!important;
  background:var(--bg3)!important; color:var(--text2)!important;
  box-shadow:var(--shadow-sm)!important; transition:all .15s ease!important;
}
.stButton>button:hover {
  transform:translate(2px,2px)!important; box-shadow:none!important;
  border-color:var(--accent)!important; color:var(--accent)!important; background:rgba(16,185,129,.08)!important;
}
.stButton>button:active { transform:translate(2px,2px)!important; box-shadow:none!important; }
.stButton>button[kind="primary"] {
  font-family:var(--font-display)!important; font-weight:700!important;
  background:var(--accent)!important; color:var(--black)!important;
  border:2px solid var(--accent)!important; box-shadow:2px 2px 0px rgba(16,185,129,0.4)!important;
}
.stButton>button[kind="primary"]:hover {
  transform:translate(2px,2px)!important; box-shadow:none!important;
  background:var(--accent)!important; color:var(--black)!important;
}

/* Inputs */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input {
  font-family:var(--font-body)!important; background:var(--bg3)!important;
  color:var(--text)!important; border:2px solid var(--g800)!important;
  border-radius:0!important; font-size:.9rem!important; transition:all .2s!important;
}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus {
  border-color:var(--accent)!important; box-shadow:none!important;
  outline:2px solid rgba(16,185,129,.3)!important; outline-offset:0!important;
}
[data-testid="stSelectbox"]>div>div { background:var(--bg3)!important; border:2px solid var(--g800)!important; border-radius:0!important; color:var(--text)!important; }

/* Tabs */
[data-testid="stTabs"] { border-bottom:2px solid var(--g800)!important; }
[data-testid="stTabs"] button { font-family:var(--font-body)!important; color:var(--text3)!important; font-weight:600!important; padding:.7rem 1.25rem!important; border-radius:0!important; }
[data-testid="stTabs"] button[aria-selected="true"] { font-family:var(--font-display)!important; color:var(--accent)!important; border-bottom:3px solid var(--accent)!important; font-weight:700!important; background:rgba(16,185,129,.05)!important; }

/* Alerts */
[data-testid="stAlert"] { border-radius:0!important; border-width:2px!important; box-shadow:var(--shadow-sm)!important; }

/* DataFrame */
[data-testid="stDataFrame"] { border-radius:0!important; overflow:hidden!important; border:2px solid var(--g800)!important; box-shadow:var(--shadow)!important; }
[data-testid="stDataFrame"] th { font-family:var(--font-mono)!important; background:var(--g900)!important; color:var(--g400)!important; font-size:.7rem!important; text-transform:uppercase; font-weight:500!important; letter-spacing:.08em!important; }
[data-testid="stDataFrame"] td { color:var(--text)!important; font-family:var(--font-body)!important; }
[data-testid="stDataFrame"] tr:hover td { background:var(--bg3)!important; }

/* Expander */
[data-testid="stExpander"] { background:var(--bg2)!important; border:2px solid var(--g800)!important; border-radius:0!important; box-shadow:var(--shadow-sm)!important; margin-bottom:.75rem!important; }
[data-testid="stExpander"] summary { font-family:var(--font-display)!important; color:var(--text)!important; font-weight:700!important; }

/* Progress */
.stProgress>div>div>div { background:var(--accent)!important; border-radius:0!important; }
.stProgress>div>div { background:var(--bg4)!important; border-radius:0!important; border:1px solid var(--g800)!important; }

/* File uploader */
[data-testid="stFileUploader"] { border:2px dashed var(--g700)!important; border-radius:0!important; background:var(--bg2)!important; padding:1.5rem!important; }

/* Misc */
[data-testid="stCheckbox"] label,[data-testid="stRadio"] label { color:var(--text)!important; }
[data-testid="stToggle"] label { color:var(--text)!important; font-weight:600!important; }
.js-plotly-plot .plotly .main-svg { background:transparent!important; }
hr { border:none!important; border-top:2px solid var(--g800)!important; margin:1.5rem 0!important; }

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:var(--bg2); }
::-webkit-scrollbar-thumb { background:var(--g700); }

@media (max-width:768px) {
  [data-testid="stHorizontalBlock"] { flex-direction:column!important; }
  [data-testid="column"]:first-of-type { position:relative!important; max-height:none!important; min-height:auto!important; border-right:none!important; border-bottom:2px solid var(--g800)!important; overflow-y:visible!important; }
  [data-testid="stMetricValue"] { font-size:1.7rem!important; }
  h1 { font-size:1.5rem!important; }
}
</style>
"""
