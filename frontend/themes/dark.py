DARK_THEME = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #4A9EFF;
        --primary-glow: rgba(74, 158, 255, 0.5);
        --primary-bright: #60B0FF;
        --secondary: #9F7AEA;
        --success: #00d68f;
        --success-glow: rgba(0, 214, 143, 0.5);
        --warning: #ffab00;
        --warning-glow: rgba(255, 171, 0, 0.5);
        --danger: #ff5252;
        --danger-glow: rgba(255, 82, 82, 0.5);
        --info: #4A9EFF;
        --cyan: #00d4ff;
        --pink: #ff2d95;
        
        --dark: #0a0e1a;
        --dark-secondary: #141824;
        --dark-tertiary: #1a1f2e;
        --dark-quaternary: #252b3b;
        --dark-elevated: #2d3548;
        
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --text-tertiary: #718096;
        --text-muted: #4a5568;
        
        --border: #2d3748;
        --border-light: #3d4758;
        --border-bright: rgba(74, 158, 255, 0.3);
        
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
        --shadow-md: 0 10px 15px rgba(0, 0, 0, 0.5);
        --shadow-lg: 0 20px 25px rgba(0, 0, 0, 0.6);
        --shadow-xl: 0 25px 50px rgba(0, 0, 0, 0.7);
        
        --glow-sm: 0 0 10px var(--primary-glow);
        --glow-md: 0 0 20px var(--primary-glow);
        --glow-lg: 0 0 40px var(--primary-glow);
        
        --glass-bg: rgba(20, 24, 36, 0.7);
        --glass-border: rgba(74, 158, 255, 0.2);
        --glass-bright: rgba(26, 31, 46, 0.8);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 50%, #0a0e1a 100%);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 400;
        line-height: 1.6;
        position: relative;
        overflow-x: hidden;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(74, 158, 255, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(0, 214, 143, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(159, 122, 234, 0.06) 0%, transparent 50%);
        animation: backgroundShift 30s ease infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes backgroundShift {
        0%, 100% { transform: translate(0, 0); }
        25% { transform: translate(-5%, 5%); }
        50% { transform: translate(-10%, 0); }
        75% { transform: translate(-5%, -5%); }
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(74, 158, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(74, 158, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.3;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    [data-testid="stSidebar"] {
        background: var(--glass-bg);
        backdrop-filter: blur(30px) saturate(180%);
        -webkit-backdrop-filter: blur(30px) saturate(180%);
        border-right: 1px solid var(--glass-border);
        box-shadow: 4px 0 40px rgba(0, 0, 0, 0.5), inset -1px 0 0 rgba(74, 158, 255, 0.1);
        position: relative;
        z-index: 100;
    }
    
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 1px;
        height: 100%;
        background: linear-gradient(180deg, transparent 0%, var(--primary) 50%, transparent 100%);
        opacity: 0.5;
        animation: sidebarGlow 3s ease infinite;
    }
    
    @keyframes sidebarGlow {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.7; }
    }
    
    [data-testid="stSidebar"] label {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 10px;
        padding: 0.625rem 1rem;
        position: relative;
    }
    
    [data-testid="stSidebar"] label:hover {
        background: rgba(74, 158, 255, 0.1);
        color: var(--primary);
        transform: translateX(6px);
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.2);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 2rem;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(74, 158, 255, 0.4), 0 0 40px rgba(74, 158, 255, 0.2);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.6s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-bright) 0%, #a855f7 100%);
        box-shadow: 0 6px 30px rgba(74, 158, 255, 0.6), 0 0 60px rgba(74, 158, 255, 0.4);
        transform: translateY(-3px) scale(1.02);
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, var(--dark-tertiary) 0%, var(--dark-secondary) 100%);
        border: 2px solid var(--border);
        border-radius: 12px;
        color: var(--text-primary);
        padding: 0.875rem 1.125rem;
        transition: all 0.4s ease;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(74, 158, 255, 0.15), 0 0 30px rgba(74, 158, 255, 0.3);
        outline: none;
    }
    
    .metric-card {
        background: var(--glass-bright);
        backdrop-filter: blur(30px) saturate(180%);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 2rem;
        margin: 0.875rem 0;
        box-shadow: var(--shadow-md);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--cyan), var(--success), var(--pink));
        background-size: 300% 100%;
        animation: rainbowShift 6s linear infinite;
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    @keyframes rainbowShift {
        0% { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }
    
    .metric-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-lg), 0 0 40px rgba(74, 158, 255, 0.3);
        transform: translateY(-8px) scale(1.02);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-title {
        color: var(--text-secondary);
        font-size: 0.8125rem;
        font-weight: 700;
        margin-bottom: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        text-shadow: 0 0 10px rgba(74, 158, 255, 0.2);
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: 0.625rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 50%, var(--success) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% 200%;
        animation: gradientFlow 4s ease infinite;
        letter-spacing: -0.03em;
    }
    
    @keyframes gradientFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .metric-delta {
        color: var(--success);
        font-size: 0.9375rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.875rem;
        background: rgba(0, 214, 143, 0.15);
        border-radius: 20px;
        border: 1px solid rgba(0, 214, 143, 0.3);
        box-shadow: 0 0 20px rgba(0, 214, 143, 0.2);
    }
    
    .metric-delta.negative {
        color: var(--danger);
        background: rgba(255, 82, 82, 0.15);
        border-color: rgba(255, 82, 82, 0.3);
        box-shadow: 0 0 20px rgba(255, 82, 82, 0.2);
    }
    
    .metric-delta::before {
        content: '↗';
        font-size: 1.125rem;
        animation: bounce 2s ease infinite;
    }
    
    .metric-delta.negative::before {
        content: '↘';
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    
    .main-header {
        font-size: 2.75rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 50%, var(--success) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite, fadeInDown 0.6s ease;
        letter-spacing: -0.03em;
        text-shadow: 0 0 40px rgba(74, 158, 255, 0.5);
        filter: drop-shadow(0 0 30px rgba(74, 158, 255, 0.4));
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
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.625rem;
        background: var(--dark-tertiary);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-radius: 8px;
        color: var(--text-secondary);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(74, 158, 255, 0.1);
        color: var(--primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
        color: var(--primary);
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .streamlit-expanderHeader {
        background: var(--glass-bright);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 600;
        padding: 1.125rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--dark-tertiary);
        border-color: var(--primary);
        box-shadow: 0 0 30px rgba(74, 158, 255, 0.2);
        transform: translateX(4px);
    }
    
    .alert {
        border-radius: 12px;
        padding: 1.125rem 1.5rem;
        margin: 1.25rem 0;
        border-left: 4px solid;
        animation: slideInRight 0.4s ease;
        box-shadow: var(--shadow);
        backdrop-filter: blur(10px);
    }
    
    .alert-success {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.15) 0%, rgba(0, 214, 143, 0.05) 100%);
        border-left-color: var(--success);
        color: var(--success);
        box-shadow: 0 0 30px rgba(0, 214, 143, 0.2);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 171, 0, 0.15) 0%, rgba(255, 171, 0, 0.05) 100%);
        border-left-color: var(--warning);
        color: var(--warning);
        box-shadow: 0 0 30px rgba(255, 171, 0, 0.2);
    }
    
    .alert-error {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.15) 0%, rgba(255, 82, 82, 0.05) 100%);
        border-left-color: var(--danger);
        color: var(--danger);
        box-shadow: 0 0 30px rgba(255, 82, 82, 0.2);
    }
    
    .alert-info {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.15) 0%, rgba(74, 158, 255, 0.05) 100%);
        border-left-color: var(--info);
        color: var(--info);
        box-shadow: 0 0 30px rgba(74, 158, 255, 0.2);
    }
    
    [data-testid="stFileUploader"] {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 2px dashed var(--primary);
        border-radius: 16px;
        padding: 2.5rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--cyan);
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%);
        box-shadow: 0 0 40px rgba(74, 158, 255, 0.3);
        transform: scale(1.01);
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--cyan) 50%, var(--success) 100%);
        background-size: 200% 100%;
        border-radius: 10px;
        height: 10px;
        animation: progressShine 2s ease infinite;
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.5);
    }
    
    @keyframes progressShine {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .stProgress > div > div {
        background-color: var(--dark-tertiary);
        border-radius: 10px;
        height: 10px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stDataFrame"] {
        background: var(--dark-tertiary);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
    }
    
    .stDataFrame thead tr {
        background: linear-gradient(135deg, var(--dark-quaternary) 0%, var(--dark-tertiary) 100%);
        border-bottom: 2px solid var(--primary);
    }
    
    .stDataFrame tbody tr:hover {
        background: linear-gradient(90deg, rgba(74, 158, 255, 0.1) 0%, transparent 100%);
    }
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--dark-secondary);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 100%);
        border-radius: 10px;
        border: 2px solid var(--dark-secondary);
        box-shadow: 0 0 10px rgba(74, 158, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-bright) 0%, #00e5ff 100%);
        box-shadow: 0 0 15px rgba(74, 158, 255, 0.7);
    }
    
    code {
        background: linear-gradient(135deg, var(--dark-tertiary) 0%, var(--dark-quaternary) 100%);
        color: var(--cyan);
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.875em;
        font-weight: 500;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
    }
    
    .login-container {
        max-width: 480px;
        margin: 4rem auto;
        padding: 3rem;
        background: var(--glass-bright);
        backdrop-filter: blur(30px) saturate(180%);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: var(--shadow-xl), 0 0 60px rgba(74, 158, 255, 0.2);
        animation: fadeInUp 0.6s ease;
        position: relative;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        inset: -2px;
        background: linear-gradient(135deg, var(--primary), var(--cyan), var(--pink));
        border-radius: 24px;
        z-index: -1;
        opacity: 0.5;
        filter: blur(20px);
    }
    
    .login-logo {
        text-align: center;
        font-size: 4.5rem;
        margin-bottom: 1.5rem;
        animation: bounce 1s ease, glow 2s ease infinite;
        filter: drop-shadow(0 0 30px rgba(74, 158, 255, 0.6));
    }
    
    @keyframes glow {
        0%, 100% { filter: drop-shadow(0 0 30px rgba(74, 158, 255, 0.6)); }
        50% { filter: drop-shadow(0 0 50px rgba(74, 158, 255, 0.9)); }
    }
    
    .login-title {
        text-align: center;
        font-size: 2.25rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
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
    
    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .metric-value { font-size: 1.75rem; }
        .login-container { margin: 2rem 1rem; padding: 2rem; }
    }
</style>
"""