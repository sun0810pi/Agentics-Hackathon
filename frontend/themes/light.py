LIGHT_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #f0f4ff;
    --bg2:      #ffffff;
    --bg3:      #f1f5fb;
    --bg4:      #e8edf5;
    --primary:  #2563eb;
    --cyan:     #0891b2;
    --green:    #059669;
    --yellow:   #d97706;
    --red:      #dc2626;
    --text:     #0f172a;
    --text2:    #64748b;
    --text3:    #94a3b8;
    --border:   rgba(0,0,0,0.07);
    --border2:  rgba(37,99,235,0.22);
    --radius:   12px;
}

#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebarNav"],[data-testid="stStatusWidget"]{display:none!important;}

html,body{margin:0!important;padding:0!important;}
*,*::before,*::after{box-sizing:border-box;}

.stApp{font-family:'Inter',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;margin:0!important;padding:0!important;}

/* Animated orbs */
.stApp::before{content:'';position:fixed;top:-200px;left:-200px;width:700px;height:700px;border-radius:50%;background:radial-gradient(circle at center,rgba(37,99,235,0.08) 0%,transparent 65%);animation:orbA 12s ease-in-out infinite;pointer-events:none;z-index:0;}
.stApp::after{content:'';position:fixed;bottom:-150px;right:-150px;width:600px;height:600px;border-radius:50%;background:radial-gradient(circle at center,rgba(8,145,178,0.07) 0%,transparent 65%);animation:orbB 15s ease-in-out infinite;pointer-events:none;z-index:0;}
@keyframes orbA{0%,100%{transform:translate(0,0);}33%{transform:translate(80px,60px);}66%{transform:translate(-40px,100px);}}
@keyframes orbB{0%,100%{transform:translate(0,0);}40%{transform:translate(-80px,-60px);}70%{transform:translate(50px,-40px);}}

.stApp>[data-testid="stAppViewContainer"]{padding:0!important;margin:0!important;position:relative;z-index:1;}
.stApp>[data-testid="stAppViewContainer"]>section.main{padding:0!important;margin:0!important;padding-left:0!important;}
.main{padding:0!important;margin:0!important;padding-left:0!important;}
.main .block-container{padding:0!important;padding-left:0!important;max-width:100%!important;margin:0!important;width:100%!important;}
section.main>div{padding:0!important;margin:0!important;}

[data-testid="stHorizontalBlock"]{gap:0!important;padding:0!important;margin:0!important;align-items:stretch!important;width:100%!important;}
[data-testid="stHorizontalBlock"]>div{padding:0!important;margin:0!important;}

[data-testid="column"]:first-of-type{background:#ffffff!important;border-right:1px solid rgba(0,0,0,0.09)!important;box-shadow:2px 0 16px rgba(0,0,0,0.05)!important;min-height:100vh!important;position:sticky!important;top:0!important;overflow-y:auto!important;max-height:100vh!important;}
[data-testid="column"]:last-of-type{background:transparent!important;min-height:100vh!important;}

h1{font-size:1.75rem!important;font-weight:700!important;color:var(--text)!important;letter-spacing:-.025em!important;margin-bottom:.5rem!important;}
h2{font-size:1.3rem!important;font-weight:600!important;color:var(--text)!important;margin-top:2rem!important;margin-bottom:.5rem!important;}
h3{font-size:1.05rem!important;font-weight:600!important;color:var(--text)!important;margin-top:1.75rem!important;margin-bottom:.4rem!important;}
h4{font-size:.9rem!important;font-weight:600!important;color:var(--text2)!important;text-transform:uppercase;letter-spacing:.06em;}
p,span,li{color:var(--text)!important;}
label{color:var(--text2)!important;font-size:.78rem!important;font-weight:500!important;text-transform:uppercase;letter-spacing:.06em;}

.stButton>button{font-family:'Inter',sans-serif!important;font-weight:500!important;font-size:.875rem!important;border-radius:8px!important;border:1px solid var(--border)!important;background:var(--bg3)!important;color:var(--text2)!important;transition:all .15s!important;box-shadow:0 1px 2px rgba(0,0,0,0.05)!important;}
.stButton>button:hover{border-color:var(--border2)!important;color:var(--primary)!important;background:rgba(37,99,235,0.04)!important;transform:translateY(-1px)!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,var(--primary),#1d4ed8)!important;border:1px solid rgba(37,99,235,0.3)!important;color:#fff!important;font-weight:600!important;box-shadow:0 2px 12px rgba(37,99,235,0.28)!important;}
.stButton>button[kind="primary"]:hover{box-shadow:0 4px 18px rgba(37,99,235,0.4)!important;transform:translateY(-1px)!important;color:#fff!important;}

.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:var(--bg2)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:8px!important;box-shadow:0 1px 2px rgba(0,0,0,0.04)!important;}
.stTextInput>div>div>input:focus{border-color:var(--primary)!important;box-shadow:0 0 0 3px rgba(37,99,235,0.1)!important;}
[data-testid="stSelectbox"]>div>div{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:8px!important;}

[data-testid="stMetric"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:1.35rem 1.5rem!important;box-shadow:0 2px 8px rgba(0,0,0,0.05)!important;position:relative;overflow:hidden;margin-bottom:.25rem!important;}
[data-testid="stMetric"]:hover{box-shadow:0 4px 16px rgba(37,99,235,0.1)!important;}
[data-testid="stMetric"]::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--primary),var(--cyan));opacity:.5;}
[data-testid="stMetricLabel"]>div{color:var(--text2)!important;font-size:.72rem!important;text-transform:uppercase!important;letter-spacing:.1em!important;font-weight:500!important;}
[data-testid="stMetricValue"]{color:var(--text)!important;font-size:2.1rem!important;font-weight:700!important;letter-spacing:-.025em!important;}

hr{border:none!important;border-top:1px solid var(--border)!important;margin:1.75rem 0!important;}
[data-testid="stExpander"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;box-shadow:0 1px 4px rgba(0,0,0,0.04)!important;margin-bottom:.75rem!important;}
[data-testid="stTabs"]{border-bottom:1px solid var(--border)!important;}
[data-testid="stTabs"] button{color:var(--text2)!important;font-weight:500!important;}
[data-testid="stTabs"] button[aria-selected="true"]{color:var(--primary)!important;border-bottom:2px solid var(--primary)!important;font-weight:600!important;}
[data-testid="stAlert"]{border-radius:var(--radius)!important;margin-bottom:1.25rem!important;}
[data-testid="stDataFrame"]{border-radius:var(--radius)!important;overflow:hidden!important;}
[data-testid="stDataFrame"] th{background:var(--bg3)!important;color:var(--text2)!important;font-size:.72rem!important;text-transform:uppercase;}
[data-testid="stFileUploader"]{border:2px dashed var(--border)!important;border-radius:var(--radius)!important;background:var(--bg3)!important;padding:1.5rem!important;}
.stProgress>div>div>div{background:linear-gradient(90deg,var(--primary),var(--cyan))!important;border-radius:99px!important;}
.stProgress>div>div{background:var(--bg3)!important;border-radius:99px!important;}
[data-testid="stCheckbox"] label,[data-testid="stRadio"] label{color:var(--text)!important;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:rgba(0,0,0,.12);border-radius:2px;}

@media(max-width:768px){
[data-testid="column"]:first-of-type{position:relative!important;max-height:none!important;min-height:auto!important;border-right:none!important;border-bottom:1px solid var(--border)!important;}
[data-testid="stMetricValue"]{font-size:1.6rem!important;}h1{font-size:1.4rem!important;}
}

/* ═══════════════════════════════════════════════════════
   FIX 4: SIDEBAR SÁT VIỀN
   ═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem !important;
}

section[data-testid="stSidebar"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-left: 0 !important;
}

/* ═══════════════════════════════════════════════════════
   FIX 5: PAGE FEATURES SPACING
   ═══════════════════════════════════════════════════════ */
.main h1, .main h2, .main h3 {
    margin-top: 2.5rem !important;
    margin-bottom: 1.5rem !important;
}

.main h1:first-child, .main h2:first-child {
    margin-top: 1rem !important;
}

[data-testid="metric-container"],
[data-testid="stMetric"] {
    margin-bottom: 1.5rem !important;
}

[data-testid="stPlotlyChart"],
.element-container:has(iframe) {
    margin-bottom: 2rem !important;
}

[data-testid="stDataFrame"] {
    margin: 2rem 0 !important;
}

[data-testid="stExpander"] {
    margin: 1.5rem 0 !important;
}

[data-testid="stTabs"] {
    margin: 2rem 0 !important;
}

[data-testid="stAlert"] {
    margin: 1.5rem 0 !important;
}

[data-testid="column"] {
    padding: 0 1rem !important;
}

[data-testid="column"]:first-child {
    padding-left: 0 !important;
}

[data-testid="column"]:last-child {
    padding-right: 0 !important;
}

hr {
    margin: 3rem 0 !important;
    opacity: 0.15 !important;
}

.element-container {
    margin-bottom: 1.5rem !important;
}

</style>
"""
