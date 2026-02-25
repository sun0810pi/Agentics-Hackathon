LIGHT_THEME = """
<style>
    /* =====================================================
       IMPORTS & FONTS
       ===================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* =====================================================
       ROOT VARIABLES
       ===================================================== */
    :root {
        --primary: #2563eb;
        --primary-hover: #1d4ed8;
        --primary-light: #dbeafe;
        --success: #10b981;
        --success-light: #d1fae5;
        --warning: #f59e0b;
        --warning-light: #fef3c7;
        --danger: #ef4444;
        --danger-light: #fee2e2;
        --info: #3b82f6;
        --info-light: #dbeafe;
        
        --light: #ffffff;
        --light-secondary: #f8fafc;
        --light-tertiary: #f1f5f9;
        --light-quaternary: #e2e8f0;
        
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-tertiary: #94a3b8;
        
        --border: #e2e8f0;
        --border-hover: #cbd5e1;
        
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.8);
    }
    
    /* =====================================================
       BASE STYLES
       ===================================================== */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 400;
        line-height: 1.6;
        letter-spacing: -0.01em;
    }
    
    /* Background pattern */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(37, 99, 235, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(245, 158, 11, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Sidebar toggle - must override header visibility:hidden */
    section[data-testid="stSidebarCollapsedControl"],
    section[data-testid="stSidebarCollapsedControl"] *,
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] * {
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    
    /* =====================================================
       SIDEBAR - GLASSMORPHISM
       ===================================================== */
    [data-testid="stSidebar"] {
        background: var(--glass-bg);
        border-right: 1px solid var(--glass-border);
        box-shadow: var(--shadow-lg);
        z-index: 100;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary);
        font-weight: 700;
    }
    
    /* Sidebar navigation items */
    [data-testid="stSidebar"] .stRadio > div {
        background: transparent;
    }
    
    [data-testid="stSidebar"] label {
        transition: all 0.2s ease;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #0f172a !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown div,
    [data-testid="stSidebar"] span {
        color: #0f172a !important;
    }
    
    [data-testid="stSidebar"] label:hover {
        background: rgba(37, 99, 235, 0.08);
        color: var(--primary);
        transform: translateX(4px);
    }
    
    /* =====================================================
       BUTTONS - MODERN & ANIMATED
       ===================================================== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.25);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-hover) 0%, #1e40af 100%);
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px 0 rgba(37, 99, 235, 0.3);
    }
    
    /* Button variants */
    .stButton > button[kind="secondary"] {
        background: var(--light);
        border: 2px solid var(--primary);
        color: var(--primary);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--primary-light);
        border-color: var(--primary-hover);
        box-shadow: var(--shadow);
    }
    
    .stButton > button[kind="tertiary"] {
        background: transparent;
        color: var(--text-secondary);
        box-shadow: none;
    }
    
    .stButton > button[kind="tertiary"]:hover {
        background: var(--light-tertiary);
        color: var(--text-primary);
    }
    
    /* Small buttons */
    .stButton > button[size="small"] {
        padding: 0.4rem 1rem;
        font-size: 0.875rem;
    }
    
    /* =====================================================
       INPUTS & FORMS - CLEAN & MODERN
       ===================================================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div {
        background-color: var(--light);
        border: 2px solid var(--border);
        border-radius: 10px;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        outline: none;
        background-color: var(--light);
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-tertiary);
        opacity: 0.7;
        font-weight: 400;
    }
    
    /* Input labels */
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stSelectbox label,
    .stMultiSelect label {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* =====================================================
       METRIC CARDS - GLASSMORPHISM
       ===================================================== */
    .metric-card {
        background: var(--glass-bg);
        -webkit-
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.75rem;
        margin: 0.75rem 0;
        box-shadow: var(--shadow-md);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--success), var(--warning));
        border-radius: 16px 16px 0 0;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(37, 99, 235, 0.4);
        box-shadow: var(--shadow-lg);
        transform: translateY(-6px) scale(1.02);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-title {
        color: var(--text-secondary);
        font-size: 0.8125rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    
    .metric-delta {
        color: var(--success);
        font-size: 0.875rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.25rem 0.75rem;
        background: var(--success-light);
        border-radius: 20px;
    }
    
    .metric-delta.negative {
        color: var(--danger);
        background: var(--danger-light);
    }
    
    .metric-delta::before {
        content: '↗';
        font-size: 1.125rem;
        font-weight: 900;
    }
    
    .metric-delta.negative::before {
        content: '↘';
    }
    
    /* =====================================================
       HEADERS - GRADIENT TEXT
       ===================================================== */
    .main-header {
        font-size: 2.75rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary) 0%, var(--success) 50%, var(--warning) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
        letter-spacing: -0.03em;
        animation: fadeInDown 0.6s ease, gradientShift 8s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .sub-header {
        color: var(--text-secondary);
        font-size: 1.125rem;
        margin-bottom: 2.5rem;
        font-weight: 500;
        animation: fadeInUp 0.6s ease;
        line-height: 1.7;
    }
    
    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.25rem; }
    
    /* =====================================================
       TABS - MODERN PILL STYLE
       ===================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: var(--light-tertiary);
        border-radius: 12px;
        padding: 0.375rem;
        box-shadow: inset var(--shadow-sm);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        border-radius: 8px;
        color: var(--text-secondary);
        padding: 0.65rem 1.5rem;
        font-weight: 600;
        font-size: 0.9375rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(37, 99, 235, 0.08);
        color: var(--primary);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--light);
        color: var(--primary);
        box-shadow: var(--shadow-sm);
    }
    
    /* Tab content */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }
    
    /* =====================================================
       EXPANDER - ACCORDION STYLE
       ===================================================== */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 600;
        padding: 1.125rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--light);
        border-color: var(--primary);
        box-shadow: var(--shadow);
        transform: translateX(4px);
    }
    
    .streamlit-expanderContent {
        background: var(--light);
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
    }
    
    /* =====================================================
       ALERTS & MESSAGES - MODERN STYLE
       ===================================================== */
    .alert {
        border-radius: 12px;
        padding: 1.125rem 1.5rem;
        margin: 1.25rem 0;
        border-left: 4px solid;
        animation: slideInRight 0.4s ease;
        box-shadow: var(--shadow);
        display: flex;
        align-items: start;
        gap: 1rem;
    }
    
    .alert::before {
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    
    .alert-success {
        background: linear-gradient(135deg, var(--success-light) 0%, rgba(16, 185, 129, 0.05) 100%);
        border-left-color: var(--success);
        color: #065f46;
    }
    
    .alert-success::before {
        content: '✓';
        color: var(--success);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, var(--warning-light) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left-color: var(--warning);
        color: #92400e;
    }
    
    .alert-warning::before {
        content: '⚠';
        color: var(--warning);
    }
    
    .alert-error {
        background: linear-gradient(135deg, var(--danger-light) 0%, rgba(239, 68, 68, 0.05) 100%);
        border-left-color: var(--danger);
        color: #991b1b;
    }
    
    .alert-error::before {
        content: '✕';
        color: var(--danger);
    }
    
    .alert-info {
        background: linear-gradient(135deg, var(--info-light) 0%, rgba(59, 130, 246, 0.05) 100%);
        border-left-color: var(--info);
        color: #1e40af;
    }
    
    .alert-info::before {
        content: 'ℹ';
        color: var(--info);
    }
    
    /* Streamlit native alerts */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: var(--shadow);
        padding: 1rem 1.25rem;
    }
    
    /* =====================================================
       FILE UPLOADER - DRAG & DROP
       ===================================================== */
    [data-testid="stFileUploader"] {
        background: var(--glass-bg);
        border: 2px dashed var(--primary);
        border-radius: 16px;
        padding: 2.5rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--success);
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.03) 0%, rgba(16, 185, 129, 0.03) 100%);
        box-shadow: var(--shadow-md);
        transform: scale(1.01);
    }
    
    [data-testid="stFileUploader"] section {
        border: none;
        background-color: transparent;
    }
    
    [data-testid="stFileUploader"] button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.625rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background: var(--primary-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow);
    }
    
    /* =====================================================
       PROGRESS BAR - ANIMATED GRADIENT
       ===================================================== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, 
            var(--primary) 0%, 
            var(--success) 50%, 
            var(--primary) 100%
        );
        background-size: 200% 100%;
        border-radius: 10px;
        height: 10px;
        animation: progressShine 2s ease infinite;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }
    
    @keyframes progressShine {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .stProgress > div > div {
        background-color: var(--light-tertiary);
        border-radius: 10px;
        height: 10px;
        box-shadow: inset var(--shadow-sm);
    }
    
    /* Progress text */
    .stProgress > div > div > div:first-child {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* =====================================================
       DATAFRAME & TABLES - MODERN GRID
       ===================================================== */
    [data-testid="stDataFrame"] {
        background: var(--light);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
    }
    
    .stDataFrame table {
        background-color: var(--light);
        color: var(--text-primary);
    }
    
    .stDataFrame thead tr {
        background: linear-gradient(135deg, var(--light-tertiary) 0%, var(--light-secondary) 100%);
        border-bottom: 2px solid var(--primary);
    }
    
    .stDataFrame thead th {
        color: var(--text-primary);
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.8125rem;
        letter-spacing: 0.05em;
        padding: 1rem;
    }
    
    .stDataFrame tbody td {
        padding: 0.875rem 1rem;
        border-bottom: 1px solid var(--border);
    }
    
    .stDataFrame tbody tr:hover {
        background: linear-gradient(90deg, rgba(37, 99, 235, 0.05) 0%, transparent 100%);
    }
    
    .stDataFrame tbody tr:last-child td {
        border-bottom: none;
    }
    
    /* =====================================================
       METRICS (st.metric) - ENHANCED
       ===================================================== */
    [data-testid="stMetricValue"] {
        font-size: 2.25rem;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary);
        text-transform: uppercase;
        font-size: 0.8125rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 700;
        font-size: 0.9375rem;
        padding: 0.25rem 0.625rem;
        border-radius: 16px;
        display: inline-block;
    }
    
    [data-testid="stMetricDelta"] svg {
        fill: var(--success);
    }
    
    [data-testid="stMetricDelta"]:not([data-negative="true"]) {
        background: var(--success-light);
        color: var(--success);
    }
    
    [data-testid="stMetricDelta"][data-negative="true"] {
        background: var(--danger-light);
        color: var(--danger);
    }
    
    [data-testid="stMetricDelta"][data-negative="true"] svg {
        fill: var(--danger);
    }
    
    /* =====================================================
       SCROLLBAR - CUSTOM STYLED
       ===================================================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--light-tertiary);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
        border-radius: 10px;
        border: 2px solid var(--light-tertiary);
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-hover) 0%, #059669 100%);
    }
    
    /* =====================================================
       SPINNER & LOADING
       ===================================================== */
    .stSpinner > div {
        border-top-color: var(--primary);
        border-right-color: var(--success);
        border-bottom-color: var(--warning);
        animation: spin 0.8s linear infinite;
    }
    
    /* =====================================================
       CODE BLOCKS - SYNTAX HIGHLIGHTING STYLE
       ===================================================== */
    code {
        background: linear-gradient(135deg, var(--light-tertiary) 0%, var(--light-quaternary) 100%);
        color: var(--primary);
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.875em;
        font-weight: 500;
        border: 1px solid var(--border);
    }
    
    pre {
        background: var(--light);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        overflow-x: auto;
        box-shadow: var(--shadow-sm);
    }
    
    pre code {
        background: transparent;
        border: none;
        padding: 0;
    }
    
    /* =====================================================
       RADIO & CHECKBOX - CUSTOM STYLED
       ===================================================== */
    .stRadio > div,
    .stCheckbox > div {
        color: var(--text-primary);
    }
    
    .stRadio label,
    .stCheckbox label {
        transition: all 0.2s ease;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        font-weight: 500;
    }
    
    .stRadio label:hover,
    .stCheckbox label:hover {
        background: var(--primary-light);
        color: var(--primary);
    }
    
    /* Radio button custom */
    .stRadio input[type="radio"] {
        accent-color: var(--primary);
    }
    
    /* Checkbox custom */
    .stCheckbox input[type="checkbox"] {
        accent-color: var(--primary);
    }
    
    /* =====================================================
       SELECT & MULTISELECT
       ===================================================== */
    .stSelectbox label,
    .stMultiSelect label {
        color: var(--text-primary);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8125rem;
        letter-spacing: 0.05em;
    }
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--light);
        border: 2px solid var(--border);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* =====================================================
       SLIDER - GRADIENT TRACK
       ===================================================== */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
        border-radius: 10px;
    }
    
    .stSlider > div > div > div {
        background: var(--light-tertiary);
        border-radius: 10px;
        height: 8px;
    }
    
    .stSlider [role="slider"] {
        background: var(--light);
        border: 3px solid var(--primary);
        box-shadow: var(--shadow);
        width: 20px;
        height: 20px;
    }
    
    .stSlider [role="slider"]:hover {
        box-shadow: var(--shadow-md);
        transform: scale(1.1);
    }
    
    /* =====================================================
       LOGIN FORM - GLASSMORPHISM
       ===================================================== */
    .login-container {
        max-width: 480px;
        margin: 4rem auto;
        padding: 3rem;
        background: var(--glass-bg);
        -webkit-
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: var(--shadow-xl);
        animation: fadeInUp 0.6s ease;
    }
    
    .login-logo {
        text-align: center;
        font-size: 4.5rem;
        margin-bottom: 1.5rem;
        animation: bounce 1s ease;
        filter: drop-shadow(0 4px 12px rgba(37, 99, 235, 0.3));
    }
    
    .login-title {
        text-align: center;
        font-size: 2.25rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }
    
    .login-subtitle {
        text-align: center;
        color: var(--text-secondary);
        margin-bottom: 2.5rem;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* =====================================================
       BADGES & TAGS
       ===================================================== */
    .badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.8125rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    
    .badge-success {
        background: var(--success-light);
        color: var(--success);
    }
    
    .badge-warning {
        background: var(--warning-light);
        color: var(--warning);
    }
    
    .badge-danger {
        background: var(--danger-light);
        color: var(--danger);
    }
    
    .badge-info {
        background: var(--info-light);
        color: var(--info);
    }
    
    /* =====================================================
       ANIMATIONS
       ===================================================== */
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-15px);
        }
    }
    
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    /* =====================================================
       UTILITY CLASSES
       ===================================================== */
    .text-center { text-align: center; }
    .text-right { text-align: right; }
    .text-left { text-align: left; }
    
    .font-bold { font-weight: 700; }
    .font-semibold { font-weight: 600; }
    .font-medium { font-weight: 500; }
    
    .text-sm { font-size: 0.875rem; }
    .text-base { font-size: 1rem; }
    .text-lg { font-size: 1.125rem; }
    .text-xl { font-size: 1.25rem; }
    
    .mt-1 { margin-top: 0.5rem; }
    .mt-2 { margin-top: 1rem; }
    .mt-3 { margin-top: 1.5rem; }
    .mt-4 { margin-top: 2rem; }
    .mt-5 { margin-top: 2.5rem; }
    
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    .mb-3 { margin-bottom: 1.5rem; }
    .mb-4 { margin-bottom: 2rem; }
    .mb-5 { margin-bottom: 2.5rem; }
    
    .p-1 { padding: 0.5rem; }
    .p-2 { padding: 1rem; }
    .p-3 { padding: 1.5rem; }
    .p-4 { padding: 2rem; }
    .p-5 { padding: 2.5rem; }
    
    .rounded { border-radius: 8px; }
    .rounded-lg { border-radius: 12px; }
    .rounded-xl { border-radius: 16px; }
    .rounded-full { border-radius: 9999px; }
    
    .shadow-sm { box-shadow: var(--shadow-sm); }
    .shadow { box-shadow: var(--shadow); }
    .shadow-md { box-shadow: var(--shadow-md); }
    .shadow-lg { box-shadow: var(--shadow-lg); }
    .shadow-xl { box-shadow: var(--shadow-xl); }
    
    /* =====================================================
       RESPONSIVE DESIGN
       ===================================================== */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 1.75rem;
        }
        
        .login-container {
            margin: 2rem 1rem;
            padding: 2rem;
        }
        
        .metric-card {
            padding: 1.25rem;
        }
        
        .stButton > button {
            padding: 0.5rem 1.5rem;
            font-size: 0.875rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        
        .sub-header {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
    
    /* =====================================================
       DARK MODE SUPPORT (for system preference)
       ===================================================== */
    @media (prefers-color-scheme: dark) {
        /* If user's system is in dark mode, keep light theme readable */
        /* This ensures our light theme works well even on dark displays */
    }
    
    [data-testid="collapsedControl"],
    button[kind="header"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
        z-index: 999 !important;
    }
    
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 99999 !important;
        position: fixed !important;
        left: 0 !important;
        top: 50% !important;
        background: #ffffff !important;
        border-radius: 0 8px 8px 0 !important;
        box-shadow: 4px 0 12px rgba(0,0,0,0.15) !important;
        padding: 0.5rem !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #0f172a !important;
    }
    
    section[data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 999999 !important;
    }
    
    section[data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        background: #1e293b !important;
        border-radius: 0 8px 8px 0 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    
    section[data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        fill: #e2e8f0 !important;
        display: block !important;
    }
    
</style>
"""