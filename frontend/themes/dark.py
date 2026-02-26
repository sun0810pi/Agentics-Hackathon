DARK_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg:#060912; --bg2:#0c1020; --bg3:#111827; --bg4:#1a2234;
    --primary:#3b82f6; --cyan:#06b6d4; --green:#10b981; --yellow:#f59e0b; --red:#ef4444;
    --text:#f1f5f9; --text2:#94a3b8;
    --border:rgba(59,130,246,0.13); --border2:rgba(59,130,246,0.28);
    --radius:12px;
}

/* ── Kill Streamlit chrome ── */
#MainMenu,footer,header,
[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],[data-testid="stStatusWidget"],
[data-testid="stSidebar"],[data-testid="collapsedControl"] { display:none!important; }

html,body { margin:0!important; padding:0!important; }
*,*::before,*::after { box-sizing:border-box; }

.stApp { font-family:'Inter',sans-serif!important; background:var(--bg)!important; color:var(--text)!important; }

/* Animated orbs */
.stApp::before { content:''; position:fixed; top:-250px; left:-250px; width:700px; height:700px; border-radius:50%; background:radial-gradient(circle,rgba(59,130,246,0.10) 0%,transparent 65%); animation:orbA 14s ease-in-out infinite; pointer-events:none; z-index:0; }
.stApp::after  { content:''; position:fixed; bottom:-200px; right:-200px; width:600px; height:600px; border-radius:50%; background:radial-gradient(circle,rgba(6,182,212,0.08) 0%,transparent 65%); animation:orbB 18s ease-in-out infinite; pointer-events:none; z-index:0; }
@keyframes orbA { 0%,100%{transform:translate(0,0);} 33%{transform:translate(80px,60px);} 66%{transform:translate(-40px,90px);} }
@keyframes orbB { 0%,100%{transform:translate(0,0);} 40%{transform:translate(-70px,-55px);} 70%{transform:translate(45px,-35px);} }

/* ── Strip ALL Streamlit padding ── */
.stApp>[data-testid="stAppViewContainer"] { padding:0!important; margin:0!important; position:relative; z-index:1; }
.stApp>[data-testid="stAppViewContainer"]>section.main,
[data-testid="stMain"],
section[data-testid="stMain"] { padding:0!important; margin:0!important; }
.main,.main .block-container,[data-testid="stMainBlockContainer"],[data-testid="block-container"] {
    padding:0!important; max-width:100%!important; margin:0!important; width:100%!important;
}
section.main>div:first-child,[data-testid="stMain"]>div:first-child { padding:0!important; margin:0!important; }

/* ── Two-column layout ── */
[data-testid="stHorizontalBlock"] {
    gap:0!important; padding:0!important; margin:0!important; width:100%!important;
    align-items:flex-start!important;  /* KEY: flex-start not stretch */
}
[data-testid="stHorizontalBlock"]>div { padding:0!important; margin:0!important; }

/* Nav column: sticky, scrolls independently */
[data-testid="column"]:first-of-type {
    background:linear-gradient(180deg,#090d1a 0%,#060a14 100%)!important;
    border-right:1px solid var(--border2)!important;
    min-height:100vh!important;
    position:sticky!important; top:0!important;
    overflow-y:auto!important; max-height:100vh!important;
}
/* Content column: NO height limit, flows naturally */
[data-testid="column"]:last-of-type {
    background:transparent!important;
}

/* ── Typography ── */
h1 { font-size:1.65rem!important; font-weight:700!important; color:var(--text)!important; letter-spacing:-.025em!important; line-height:1.2!important; }
h2 { font-size:1.3rem!important; font-weight:600!important; color:var(--text)!important; }
h3 { font-size:1.05rem!important; font-weight:600!important; color:var(--text)!important; }
p,span,li { color:var(--text)!important; line-height:1.65; }
label { color:var(--text2)!important; font-size:.78rem!important; font-weight:500!important; text-transform:uppercase; letter-spacing:.06em; }
[data-testid="stCaptionContainer"] { color:var(--text2)!important; font-size:.8rem!important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background:var(--bg2)!important; border:1px solid var(--border)!important;
    border-radius:var(--radius)!important; padding:1.1rem 1.25rem 1rem!important;
    position:relative; overflow:hidden; transition:border-color .2s,box-shadow .2s;
}
[data-testid="stMetric"]:hover { border-color:var(--border2)!important; box-shadow:0 0 24px rgba(59,130,246,0.12)!important; }
[data-testid="stMetric"]::after { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--primary),var(--cyan)); opacity:.65; }
[data-testid="stMetricLabel"]>div { color:var(--text2)!important; font-size:.72rem!important; text-transform:uppercase!important; letter-spacing:.1em!important; font-weight:500!important; }
[data-testid="stMetricValue"] { color:var(--text)!important; font-size:2rem!important; font-weight:700!important; letter-spacing:-.02em!important; }
[data-testid="stMetricDelta"]>div { font-size:.8rem!important; margin-top:.3rem; }

/* ── Buttons ── */
.stButton>button { font-family:'Inter',sans-serif!important; font-weight:500!important; font-size:.875rem!important; border-radius:8px!important; border:1px solid var(--border)!important; background:var(--bg3)!important; color:var(--text2)!important; transition:all .15s!important; }
.stButton>button:hover { border-color:var(--border2)!important; color:var(--text)!important; background:var(--bg4)!important; transform:translateY(-1px)!important; }
.stButton>button[kind="primary"] { background:linear-gradient(135deg,#3b82f6,#2563eb)!important; border:1px solid rgba(59,130,246,.4)!important; color:#fff!important; font-weight:600!important; box-shadow:0 2px 14px rgba(59,130,246,.35)!important; }
.stButton>button[kind="primary"]:hover { background:linear-gradient(135deg,#60a5fa,#3b82f6)!important; box-shadow:0 4px 22px rgba(59,130,246,.5)!important; transform:translateY(-1px)!important; color:#fff!important; }

/* ── Inputs ── */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input { background:var(--bg3)!important; color:var(--text)!important; border:1px solid var(--border)!important; border-radius:8px!important; font-size:.9rem!important; }
.stTextInput>div>div>input:focus { border-color:var(--primary)!important; box-shadow:0 0 0 3px rgba(59,130,246,.12)!important; }
[data-testid="stSelectbox"]>div>div { background:var(--bg3)!important; border:1px solid var(--border)!important; border-radius:8px!important; color:var(--text)!important; }

/* ── Divider ── */
hr { border:none!important; border-top:1px solid var(--border)!important; margin:1.25rem 0!important; }

/* ── Tabs ── */
[data-testid="stTabs"] { border-bottom:1px solid var(--border)!important; }
[data-testid="stTabs"] button { color:var(--text2)!important; font-weight:500!important; padding:.7rem 1.25rem!important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:var(--primary)!important; border-bottom:2px solid var(--primary)!important; font-weight:600!important; }

/* ── Alerts ── */
[data-testid="stAlert"] { border-radius:var(--radius)!important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"] { border-radius:var(--radius)!important; overflow:hidden!important; }
[data-testid="stDataFrame"] th { background:var(--bg3)!important; color:var(--text2)!important; font-size:.72rem!important; text-transform:uppercase; }
[data-testid="stDataFrame"] td { color:var(--text)!important; }

/* ── Misc ── */
[data-testid="stExpander"] { background:var(--bg2)!important; border:1px solid var(--border)!important; border-radius:var(--radius)!important; margin-bottom:.75rem!important; }
.stProgress>div>div>div { background:linear-gradient(90deg,var(--primary),var(--cyan))!important; border-radius:99px!important; }
.stProgress>div>div { background:var(--bg3)!important; border-radius:99px!important; }
[data-testid="stFileUploader"] { border:2px dashed var(--border)!important; border-radius:var(--radius)!important; background:var(--bg2)!important; padding:1.5rem!important; }
[data-testid="stCheckbox"] label,[data-testid="stRadio"] label { color:var(--text)!important; }
code { background:var(--bg3)!important; color:var(--cyan)!important; border-radius:4px; padding:1px 6px; }
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(59,130,246,.25); border-radius:2px; }

/* ── Mobile ── */
@media (max-width:768px) {
    [data-testid="stHorizontalBlock"] { flex-direction:column!important; }
    [data-testid="column"]:first-of-type { position:relative!important; max-height:none!important; min-height:auto!important; border-right:none!important; border-bottom:1px solid var(--border2)!important; overflow-y:visible!important; }
    [data-testid="stMetricValue"] { font-size:1.6rem!important; }
    h1 { font-size:1.35rem!important; }
}
</style>
"""
