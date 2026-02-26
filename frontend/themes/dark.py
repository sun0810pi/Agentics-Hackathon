DARK_THEME = """
<style>
/* STRIPPED DARK THEME - no fixed overlays, no animations */
:root {
    --primary: #4A9EFF;
    --bg: #0a0e1a;
    --bg2: #141824;
    --text: #ffffff;
    --text2: #a0aec0;
    --border: rgba(74,158,255,0.2);
    --success: #00d68f;
    --danger: #ff5252;
    --warning: #ffab00;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stSidebarNav"] {display: none !important;}

/* Background - NO position:fixed, NO ::before/::after */
.stApp {
    background-color: var(--bg);
    color: var(--text);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--bg2) !important;
    border-right: 1px solid var(--border);
}

/* Buttons */
.stButton > button {
    background: rgba(74,158,255,0.15);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
}
.stButton > button[kind="primary"] {
    background: var(--primary);
    border-color: var(--primary);
    color: white;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: var(--bg2) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
}

/* Divider */
hr { border-color: var(--border); }

/* Text colors */
h1, h2, h3, h4, h5, h6 { color: var(--text); }
p, span, div { color: inherit; }

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
}
</style>
"""
