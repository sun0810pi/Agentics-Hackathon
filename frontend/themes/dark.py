DARK_THEME = """
<style>
    /* ===== RESET & BASE ===== */
    .stApp {
        background-color: #0a0e1a;
        color: #ffffff;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
        border-right: 1px solid rgba(74, 158, 255, 0.2);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #4A9EFF 0%, #357ABD 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 158, 255, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #357ABD 0%, #2868A8 100%);
        box-shadow: 0 6px 20px rgba(74, 158, 255, 0.5);
        transform: translateY(-2px);
    }
    
    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
        color: #ffffff;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4A9EFF;
        box-shadow: 0 0 0 1px #4A9EFF;
    }
    
    /* ===== CARDS ===== */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #141824 100%);
        border: 1px solid rgba(74, 158, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(74, 158, 255, 0.5);
        box-shadow: 0 6px 20px rgba(74, 158, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .metric-title {
        color: #a0aec0;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .metric-delta {
        color: #00d68f;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .metric-delta.negative {
        color: #ff5252;
    }
    
    /* ===== HEADERS ===== */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4A9EFF 0%, #00d68f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        color: #a0aec0;
        font-size: 1.125rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
        color: #a0aec0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4A9EFF;
        border-color: #4A9EFF;
        color: white;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background-color: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #232937;
        border-color: #4A9EFF;
    }
    
    /* ===== ALERTS ===== */
    .alert {
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background-color: rgba(0, 214, 143, 0.1);
        border-left-color: #00d68f;
        color: #00d68f;
    }
    
    .alert-warning {
        background-color: rgba(255, 171, 0, 0.1);
        border-left-color: #ffab00;
        color: #ffab00;
    }
    
    .alert-error {
        background-color: rgba(255, 82, 82, 0.1);
        border-left-color: #ff5252;
        color: #ff5252;
    }
    
    .alert-info {
        background-color: rgba(74, 158, 255, 0.1);
        border-left-color: #4A9EFF;
        color: #4A9EFF;
    }
    
    /* ===== LOGIN FORM ===== */
    .login-container {
        max-width: 450px;
        margin: 6rem auto;
        padding: 2.5rem;
        background: linear-gradient(135deg, #1a1f2e 0%, #141824 100%);
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    .login-logo {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .login-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        text-align: center;
        color: #a0aec0;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        background-color: #1a1f2e;
        border: 2px dashed #4A9EFF;
        border-radius: 12px;
        padding: 2rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #00d68f;
        background-color: rgba(74, 158, 255, 0.05);
    }
    
    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4A9EFF 0%, #00d68f 100%);
        border-radius: 10px;
    }
    
    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {
        background-color: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
    }
    
    /* ===== METRIC (st.metric) ===== */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    [data-testid="stMetricDelta"] svg {
        fill: #00d68f;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1f2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4A9EFF;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #357ABD;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""