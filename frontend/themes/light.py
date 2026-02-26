LIGHT_THEME = """
<style>
/* STRIPPED LIGHT THEME - no fixed overlays */
:root {
    --primary: #2563eb;
    --bg: #f8fafc;
    --bg2: #ffffff;
    --text: #1a202c;
    --text2: #4a5568;
    --border: rgba(0,0,0,0.1);
    --success: #16a34a;
    --danger: #dc2626;
    --warning: #d97706;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stSidebarNav"] {display: none !important;}

.stApp {
    background-color: var(--bg);
    color: var(--text);
}

[data-testid="stSidebar"] {
    background-color: var(--bg2) !important;
    border-right: 1px solid var(--border);
}

.stButton > button {
    background: rgba(37,99,235,0.1);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
}
.stButton > button[kind="primary"] {
    background: var(--primary);
    border-color: var(--primary);
    color: white;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg2) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}

[data-testid="stMetric"] {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
}

hr { border-color: var(--border); }
h1, h2, h3, h4, h5, h6 { color: var(--text); }
</style>
"""
