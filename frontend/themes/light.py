LIGHT_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #f8faff;
    --bg2:      #ffffff;
    --bg3:      #f1f5fb;
    --bg4:      #e8edf7;
    --primary:  #2563eb;
    --cyan:     #0891b2;
    --green:    #059669;
    --yellow:   #d97706;
    --red:      #dc2626;
    --text:     #0f172a;
    --text2:    #64748b;
    --text3:    #94a3b8;
    --border:   rgba(0,0,0,0.07);
    --border2:  rgba(37,99,235,0.2);
    --card:     rgba(255,255,255,0.9);
    --glow:     0 4px 20px rgba(37,99,235,0.08);
    --radius:   12px;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarNav"],
[data-testid="stStatusWidget"] { display: none !important; }

*, *::before, *::after { box-sizing: border-box; }

.stApp { font-family: 'Inter', sans-serif !important; background: var(--bg) !important; color: var(--text) !important; }

.stApp > [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 10% -10%, rgba(37,99,235,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 110%, rgba(8,145,178,0.03) 0%, transparent 55%),
        #f8faff !important;
}

.stApp > [data-testid="stAppViewContainer"] > section.main { padding: 0 !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }

[data-testid="stHorizontalBlock"] { gap: 0 !important; padding: 0 !important; margin: 0 !important; align-items: stretch !important; width: 100% !important; }
[data-testid="stHorizontalBlock"] > div { padding: 0 !important; margin: 0 !important; }
.main { padding: 0 !important; margin: 0 !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
section.main > div:first-child { padding: 0 !important; margin: 0 !important; }

[data-testid="column"]:first-of-type {
    background: #ffffff !important;
    border-right: 1px solid rgba(0,0,0,0.08) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
    min-height: 100vh !important;
    position: sticky !important;
    top: 0 !important;
    overflow-y: auto !important;
    max-height: 100vh !important;
}
[data-testid="column"]:last-of-type { background: var(--bg) !important; min-height: 100vh !important; }

h1 { font-size: 1.75rem !important; font-weight: 700 !important; color: var(--text) !important; letter-spacing: -0.025em !important; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: var(--text) !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: var(--text) !important; }
h4 { font-size: 0.9rem !important; font-weight: 600 !important; color: var(--text2) !important; text-transform: uppercase; letter-spacing: 0.06em; }
p, span, div, li { color: var(--text) !important; }
label { color: var(--text2) !important; font-size: 0.78rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.06em; }

.stButton > button {
    font-family: 'Inter', sans-serif !important; font-weight: 500 !important; font-size: 0.875rem !important;
    border-radius: 8px !important; border: 1px solid var(--border) !important;
    background: var(--bg3) !important; color: var(--text2) !important;
    transition: all 0.15s ease !important; box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
.stButton > button:hover { border-color: var(--border2) !important; color: var(--primary) !important; background: rgba(37,99,235,0.04) !important; transform: translateY(-1px) !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, #1d4ed8 100%) !important;
    border: 1px solid rgba(37,99,235,0.3) !important; color: #fff !important; font-weight: 600 !important;
    box-shadow: 0 2px 10px rgba(37,99,235,0.25) !important;
}
.stButton > button[kind="primary"]:hover { box-shadow: 0 4px 16px rgba(37,99,235,0.35) !important; transform: translateY(-1px) !important; color: #fff !important; }

.stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input {
    background: var(--bg2) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.stTextInput > div > div > input:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important; }

[data-testid="stMetric"] {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; padding: 1.25rem 1.5rem !important;
    box-shadow: var(--glow) !important; position: relative; overflow: hidden;
    transition: box-shadow 0.2s !important;
}
[data-testid="stMetric"]::after { content:''; position:absolute; top:0;left:0;right:0; height:2px; background:linear-gradient(90deg,var(--primary),var(--cyan)); opacity:0.5; }
[data-testid="stMetricLabel"] > div { color: var(--text2) !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; font-weight: 500 !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-size: 2rem !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }
[data-testid="stExpander"] { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important; margin-bottom: 0.75rem !important; }
[data-testid="stTabs"] { border-bottom: 1px solid var(--border) !important; }
[data-testid="stTabs"] button { color: var(--text2) !important; font-weight: 500 !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color: var(--primary) !important; border-bottom: 2px solid var(--primary) !important; font-weight: 600 !important; }
[data-testid="stDataFrame"] th { background: var(--bg3) !important; color: var(--text2) !important; font-size: 0.72rem !important; text-transform: uppercase; }
[data-testid="stDataFrame"] td { color: var(--text) !important; }
[data-testid="stFileUploader"] { border: 2px dashed var(--border) !important; border-radius: var(--radius) !important; background: var(--bg3) !important; }
[data-testid="stSlider"] > div > div > div > div { background: linear-gradient(90deg,var(--primary),var(--cyan)) !important; }
.stProgress > div > div > div { background: linear-gradient(90deg,var(--primary),var(--cyan)) !important; border-radius:99px !important; }
.stProgress > div > div { background: var(--bg3) !important; border-radius:99px !important; }
[data-testid="stSelectbox"] > div > div { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label { color: var(--text) !important; }

/* ── Content spacing ────────────────────────────────────────── */
/* Gap between metric cards */
[data-testid="stMetric"] { margin-bottom: 0 !important; }
/* Space between column groups */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"] > div[data-testid] { 
    margin-bottom: 0.5rem !important;
}
/* Bigger gap between sections (h3 headers) */
h3 { margin-top: 1.75rem !important; margin-bottom: 0.5rem !important; }
h2 { margin-top: 2rem !important; margin-bottom: 0.6rem !important; }
/* Space after dividers */
hr + * { margin-top: 1.5rem !important; }
/* Dataframe spacing */
[data-testid="stDataFrame"] { margin-top: 0.5rem !important; }
/* Alert/warning box spacing */
[data-testid="stAlert"] { margin-bottom: 1.25rem !important; }
/* Caption spacing */
[data-testid="stCaptionContainer"] { margin-top: 0.35rem !important; }
/* Column gap inside content */
[data-testid="column"] + [data-testid="column"] { padding-left: 1rem !important; }

::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); border-radius: 2px; }

.badge { display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:99px;font-size:0.72rem;font-weight:600; }
.badge-green { background:rgba(5,150,105,0.1);color:#059669;border:1px solid rgba(5,150,105,0.2); }
.badge-red { background:rgba(220,38,38,0.1);color:#dc2626;border:1px solid rgba(220,38,38,0.2); }
.badge-yellow { background:rgba(217,119,6,0.1);color:#d97706;border:1px solid rgba(217,119,6,0.2); }
.badge-blue { background:rgba(37,99,235,0.1);color:#2563eb;border:1px solid rgba(37,99,235,0.2); }

@media (max-width: 768px) {
    [data-testid="column"]:first-of-type { position:relative !important; max-height:none !important; min-height:auto !important; border-right:none !important; border-bottom:1px solid var(--border) !important; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    h1 { font-size: 1.4rem !important; }
}
</style>
"""
