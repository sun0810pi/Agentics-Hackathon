LIGHT_THEME = """
<style>
    /* ===== BASE ===== */
    .stApp {
        background-color: #f7fafc;
        color: #1a202c;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #4A9EFF 0%, #357ABD 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(74, 158, 255, 0.25);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #357ABD 0%, #2868A8 100%);
        box-shadow: 0 6px 16px rgba(74, 158, 255, 0.4);
        transform: translateY(-2px);
    }
    
    /* ===== INPUTS ===== */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 1px solid #cbd5e0;
        border-radius: 8px;
        color: #1a202c;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4A9EFF;
        box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
    }
    
    /* ===== CARDS ===== */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .metric-card:hover {
        border-color: #4A9EFF;
        box-shadow: 0 4px 16px rgba(74, 158, 255, 0.15);
    }
    
    .main-header {
        color: #1a202c;
    }
    
    .sub-header {
        color: #718096;
    }
</style>
"""