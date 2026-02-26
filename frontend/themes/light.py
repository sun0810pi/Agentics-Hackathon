LIGHT_THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #f1f5f9;
    --bg2:       #ffffff;
    --bg3:       #f8fafc;
    --primary:   #2563eb;
    --primary2:  #3b82f6;
    --accent:    #0891b2;
    --success:   #059669;
    --warning:   #d97706;
    --danger:    #dc2626;
    --text:      #0f172a;
    --text2:     #64748b;
    --border:    rgba(0,0,0,0.08);
    --glass:     rgba(255,255,255,0.9);
}

* { box-sizing: border-box; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }

.stApp { background: var(--bg) !important; font-family: 'DM Sans', sans-serif; color: var(--text); }

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 20px rgba(0,0,0,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child { background: var(--bg2) !important; }

.main .block-container { padding: 2rem 2.5rem !important; max-width: 1200px; }

h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; color: var(--text) !important; font-size: 2rem !important; }
h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; color: var(--text) !important; }
p, span, div, li, label { color: var(--text) !important; }
label { color: var(--text2) !important; font-size: 0.85rem !important; font-weight: 500 !important; }

.stButton > button {
    border-radius: 8px !important; border: 1px solid var(--border) !important;
    background: var(--bg2) !important; color: var(--text2) !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    transition: all 0.2s !important; box-shadow: 0 1px 3px rgba(0,0,0,0.07) !important;
}
.stButton > button:hover { border-color: var(--primary) !important; color: var(--primary) !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    border-color: transparent !important; color: white !important; font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.92 !important; color: white !important; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: var(--bg2) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
.stTextInput > div > div > input:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important; }

[data-testid="stMetric"] {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.25rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stMetricLabel"] > div { color: var(--text2) !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important; font-weight: 700 !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

[data-testid="stExpander"] { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important; }

[data-testid="stTabs"] [data-testid="stTab"] { color: var(--text2) !important; }
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] { color: var(--primary) !important; border-bottom: 2px solid var(--primary) !important; }

table { border-collapse: collapse !important; width: 100%; }
th { background: var(--bg3) !important; color: var(--text2) !important; font-size: 0.8rem; text-transform: uppercase; padding: 0.6rem 1rem; }
td { border-bottom: 1px solid var(--border) !important; padding: 0.6rem 1rem; color: var(--text) !important; }

[data-testid="stFileUploader"] { border: 2px dashed var(--border) !important; border-radius: 12px !important; background: var(--bg3) !important; }
[data-testid="stSelectbox"] > div > div { background: var(--bg2) !important; border-color: var(--border) !important; color: var(--text) !important; }
[data-testid="stSlider"] > div > div > div { background: var(--primary) !important; }
[data-testid="stCheckbox"] span, [data-testid="stRadio"] label { color: var(--text) !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 3px; }
</style>
"""
