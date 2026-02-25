DARK_THEME = """
<style>
    /* =====================================================
       IMPORTS & FONTS
       ===================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;200;300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    /* =====================================================
       ROOT VARIABLES - CYBERPUNK NEON PALETTE
       ===================================================== */
    :root {
        /* Primary Colors - Blue Neon */
        --primary: #4A9EFF;
        --primary-dark: #3d85db;
        --primary-light: #60b0ff;
        --primary-glow: rgba(74, 158, 255, 0.6);
        --primary-dim: rgba(74, 158, 255, 0.3);
        
        /* Secondary Colors - Purple Neon */
        --secondary: #9F7AEA;
        --secondary-light: #b794f6;
        --secondary-glow: rgba(159, 122, 234, 0.6);
        
        /* Status Colors with Glow */
        --success: #00d68f;
        --success-light: #00f5a0;
        --success-glow: rgba(0, 214, 143, 0.6);
        --success-dim: rgba(0, 214, 143, 0.2);
        
        --warning: #ffab00;
        --warning-light: #ffc107;
        --warning-glow: rgba(255, 171, 0, 0.6);
        --warning-dim: rgba(255, 171, 0, 0.2);
        
        --danger: #ff5252;
        --danger-light: #ff6b6b;
        --danger-glow: rgba(255, 82, 82, 0.6);
        --danger-dim: rgba(255, 82, 82, 0.2);
        
        --info: #4A9EFF;
        --info-glow: rgba(74, 158, 255, 0.6);
        
        /* Accent Colors - Cyberpunk */
        --cyan: #00d4ff;
        --cyan-glow: rgba(0, 212, 255, 0.6);
        --pink: #ff2d95;
        --pink-glow: rgba(255, 45, 149, 0.6);
        --yellow: #ffd700;
        --yellow-glow: rgba(255, 215, 0, 0.6);
        --purple: #a855f7;
        --purple-glow: rgba(168, 85, 247, 0.6);
        
        /* Dark Shades */
        --dark: #0a0e1a;
        --dark-lighter: #0f1420;
        --dark-secondary: #141824;
        --dark-tertiary: #1a1f2e;
        --dark-quaternary: #252b3b;
        --dark-elevated: #2d3548;
        --dark-card: #1e2433;
        
        /* Text Colors */
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --text-tertiary: #718096;
        --text-muted: #4a5568;
        --text-bright: #e2e8f0;
        
        /* Border Colors */
        --border: #2d3748;
        --border-light: #3d4758;
        --border-bright: rgba(74, 158, 255, 0.4);
        --border-glow: rgba(74, 158, 255, 0.6);
        
        /* Shadow Levels */
        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.5);
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.5);
        --shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        --shadow-md: 0 8px 16px rgba(0, 0, 0, 0.6);
        --shadow-lg: 0 16px 32px rgba(0, 0, 0, 0.7);
        --shadow-xl: 0 24px 48px rgba(0, 0, 0, 0.8);
        --shadow-2xl: 0 32px 64px rgba(0, 0, 0, 0.9);
        
        /* Glow Effects */
        --glow-xs: 0 0 5px var(--primary-glow);
        --glow-sm: 0 0 10px var(--primary-glow);
        --glow-md: 0 0 20px var(--primary-glow);
        --glow-lg: 0 0 40px var(--primary-glow);
        --glow-xl: 0 0 60px var(--primary-glow);
        
        /* Glassmorphism */
        --glass-bg: rgba(20, 24, 36, 0.75);
        --glass-bg-light: rgba(26, 31, 46, 0.8);
        --glass-bg-dark: rgba(10, 14, 26, 0.9);
        --glass-border: rgba(74, 158, 255, 0.25);
        --glass-border-bright: rgba(74, 158, 255, 0.5);
        
        /* Animation Durations */
        --transition-fast: 0.15s;
        --transition-base: 0.3s;
        --transition-slow: 0.5s;
        --transition-slower: 0.8s;
    }
    
    /* =====================================================
       BASE STYLES - ANIMATED CYBER BACKGROUND
       ===================================================== */
    .stApp {
        background: linear-gradient(135deg, var(--dark) 0%, var(--dark-secondary) 25%, var(--dark-tertiary) 50%, var(--dark-secondary) 75%, var(--dark) 100%);
        background-size: 400% 400%;
        animation: gradientBackground 30s ease infinite;
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 400;
        line-height: 1.6;
        letter-spacing: -0.01em;
        position: relative;
        overflow-x: hidden;
    }
    
    @keyframes gradientBackground {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Animated radial gradients overlay */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(circle at 20% 30%, var(--primary-dim) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, var(--success-dim) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, var(--secondary-glow) 0%, transparent 60%),
            radial-gradient(circle at 90% 20%, var(--cyan-glow) 0%, transparent 55%),
            radial-gradient(circle at 10% 60%, var(--pink-glow) 0%, transparent 50%);
        animation: floatingGradients 40s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
        opacity: 0.4;
    }
    
    @keyframes floatingGradients {
        0%, 100% { 
            transform: translate(0, 0) rotate(0deg); 
            opacity: 0.4;
        }
        33% { 
            transform: translate(-5%, 5%) rotate(120deg); 
            opacity: 0.5;
        }
        66% { 
            transform: translate(5%, -5%) rotate(240deg); 
            opacity: 0.3;
        }
    }
    
    /* Cyber grid overlay */
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
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.5;
        animation: gridPulse 4s ease-in-out infinite;
    }
    
    @keyframes gridPulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ensure content is above background */
    .stApp > div {
        position: relative;
        z-index: 1;
    }
    
    /* =====================================================
       SIDEBAR - CYBERPUNK GLASSMORPHISM
       ===================================================== */
    [data-testid="stSidebar"] {
        background: var(--glass-bg);
        border-right: 1px solid var(--glass-border);
        box-shadow: 
            4px 0 60px rgba(0, 0, 0, 0.6),
            inset -1px 0 0 rgba(74, 158, 255, 0.15),
            inset 0 0 60px rgba(74, 158, 255, 0.03);
        position: relative;
        z-index: 100;
    }
    
    /* Animated glow border */
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: -1px;
        width: 2px;
        height: 100%;
        background: linear-gradient(
            180deg,
            transparent 0%,
            var(--primary) 20%,
            var(--cyan) 50%,
            var(--primary) 80%,
            transparent 100%
        );
        opacity: 0.6;
        animation: borderGlow 4s ease-in-out infinite;
    }
    
    @keyframes borderGlow {
        0%, 100% { 
            opacity: 0.4;
            filter: blur(2px);
        }
        50% { 
            opacity: 0.8;
            filter: blur(4px);
        }
    }
    
    /* Subtle scan line effect */
    [data-testid="stSidebar"]::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            0deg,
            transparent 0%,
            rgba(74, 158, 255, 0.03) 50%,
            transparent 100%
        );
        animation: scanLine 8s linear infinite;
        pointer-events: none;
    }
    
    @keyframes scanLine {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100%); }
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
        text-shadow: 0 0 20px var(--primary-glow);
        letter-spacing: -0.02em;
    }
    
    /* Sidebar navigation items */
    [data-testid="stSidebar"] .stRadio > div {
        background: transparent;
        gap: 0.5rem;
    }
    
    [data-testid="stSidebar"] label {
        transition: all var(--transition-base) cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 12px;
        padding: 0.75rem 1.25rem;
        margin: 0.25rem 0;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    /* Animated border on hover */
    [data-testid="stSidebar"] label::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 3px;
        background: linear-gradient(180deg, var(--primary), var(--cyan), var(--success));
        background-size: 100% 300%;
        transform: scaleY(0);
        transition: transform var(--transition-base) ease;
        border-radius: 0 3px 3px 0;
    }
    
    [data-testid="stSidebar"] label:hover::before {
        transform: scaleY(1);
        animation: borderRainbow 2s linear infinite;
    }
    
    @keyframes borderRainbow {
        0% { background-position: 0% 0%; }
        100% { background-position: 0% 100%; }
    }
    
    /* Glow effect on hover */
    [data-testid="stSidebar"] label::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, var(--primary-dim), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    [data-testid="stSidebar"] label:hover::after {
        transform: translateX(100%);
    }
    
    [data-testid="stSidebar"] label:hover {
        background: rgba(74, 158, 255, 0.12);
        color: var(--primary-light);
        transform: translateX(8px);
        box-shadow: 
            0 4px 20px rgba(74, 158, 255, 0.2),
            inset 0 0 20px rgba(74, 158, 255, 0.05);
    }
    
    /* Active/selected state */
    [data-testid="stSidebar"] label[data-selected="true"] {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.2), rgba(0, 212, 255, 0.2));
        color: var(--cyan);
        box-shadow: 
            0 0 30px rgba(74, 158, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* =====================================================
       BUTTONS - NEON GLOW WITH MULTIPLE VARIANTS
       ===================================================== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2.25rem;
        font-weight: 700;
        font-size: 0.9375rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        transition: all var(--transition-base) cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 4px 24px rgba(74, 158, 255, 0.4),
            0 0 40px rgba(74, 158, 255, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            inset 0 -1px 0 rgba(0, 0, 0, 0.2);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    /* Shimmer effect */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.4),
            transparent
        );
        transition: left 0.7s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Animated border */
    .stButton > button::after {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 14px;
        padding: 2px;
        background: linear-gradient(
            135deg,
            var(--primary),
            var(--cyan),
            var(--pink),
            var(--purple)
        );
        background-size: 300% 300%;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        opacity: 0;
        transition: opacity var(--transition-base);
        animation: borderRotate 4s linear infinite;
    }
    
    @keyframes borderRotate {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-light) 0%, #a855f7 100%);
        box-shadow: 
            0 6px 32px rgba(74, 158, 255, 0.6),
            0 0 60px rgba(74, 158, 255, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transform: translateY(-3px) scale(1.02);
    }
    
    .stButton > button:hover::after {
        opacity: 1;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1);
        box-shadow: 
            0 2px 16px rgba(74, 158, 255, 0.5),
            0 0 40px rgba(74, 158, 255, 0.4);
    }
    
    /* Secondary button variant */
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 2px solid var(--primary);
        color: var(--primary);
        box-shadow: 
            0 0 20px rgba(74, 158, 255, 0.3),
            inset 0 0 20px rgba(74, 158, 255, 0.08);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(74, 158, 255, 0.15);
        border-color: var(--primary-light);
        box-shadow: 
            0 0 30px rgba(74, 158, 255, 0.5),
            inset 0 0 30px rgba(74, 158, 255, 0.15);
    }
    
    /* Tertiary/ghost button */
    .stButton > button[kind="tertiary"] {
        background: transparent;
        color: var(--text-secondary);
        box-shadow: none;
        border: 1px solid var(--border);
    }
    
    .stButton > button[kind="tertiary"]:hover {
        background: var(--dark-tertiary);
        color: var(--text-primary);
        border-color: var(--border-bright);
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.2);
    }
    
    /* Small button size */
    .stButton > button[size="small"] {
        padding: 0.5rem 1.25rem;
        font-size: 0.875rem;
    }
    
    /* Large button size */
    .stButton > button[size="large"] {
        padding: 1rem 2.75rem;
        font-size: 1.0625rem;
    }
    
    /* Danger button */
    .stButton > button[data-variant="danger"] {
        background: linear-gradient(135deg, var(--danger) 0%, #dc2626 100%);
        box-shadow: 
            0 4px 24px var(--danger-glow),
            0 0 40px var(--danger-glow);
    }
    
    .stButton > button[data-variant="danger"]:hover {
        background: linear-gradient(135deg, var(--danger-light) 0%, #ef4444 100%);
        box-shadow: 
            0 6px 32px var(--danger-glow),
            0 0 60px var(--danger-glow);
    }
    
    /* Success button */
    .stButton > button[data-variant="success"] {
        background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
        box-shadow: 
            0 4px 24px var(--success-glow),
            0 0 40px var(--success-glow);
    }
    
    .stButton > button[data-variant="success"]:hover {
        background: linear-gradient(135deg, var(--success-light) 0%, #10b981 100%);
        box-shadow: 
            0 6px 32px var(--success-glow),
            0 0 60px var(--success-glow);
    }
    
    /* =====================================================
       INPUTS & FORMS - FUTURISTIC CYBER STYLE
       ===================================================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background: linear-gradient(135deg, var(--dark-tertiary) 0%, var(--dark-card) 100%);
        border: 2px solid var(--border);
        border-radius: 12px;
        color: var(--text-primary);
        padding: 0.9375rem 1.25rem;
        font-size: 0.9375rem;
        font-weight: 500;
        transition: all var(--transition-base) cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.4),
            0 0 0 0 transparent;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        background: var(--dark-tertiary);
        box-shadow: 
            0 0 0 4px rgba(74, 158, 255, 0.15),
            0 0 30px rgba(74, 158, 255, 0.3),
            inset 0 2px 4px rgba(0, 0, 0, 0.3),
            inset 0 0 40px rgba(74, 158, 255, 0.05);
        outline: none;
    }
    
    /* Animated border on focus */
    .stTextInput > div > div > input:focus::before,
    .stTextArea > div > div > textarea:focus::before {
        content: '';
        position: absolute;
        inset: -2px;
        background: linear-gradient(90deg, var(--primary), var(--cyan));
        border-radius: 14px;
        z-index: -1;
        opacity: 0.5;
        animation: borderPulse 2s ease infinite;
    }
    
    @keyframes borderPulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.7; }
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
    .stMultiSelect label,
    .stDateInput label,
    .stTimeInput label {
        color: var(--text-bright);
        font-weight: 700;
        font-size: 0.8125rem;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        text-shadow: 0 0 10px rgba(74, 158, 255, 0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input group styling */
    .stTextInput > div,
    .stTextArea > div,
    .stNumberInput > div {
        position: relative;
    }
    
    /* =====================================================
       METRIC CARDS - NEON GLASSMORPHISM WITH ANIMATIONS
       ===================================================== */
    .metric-card {
        background: var(--glass-bg-light);
        -webkit-
        border: 1px solid var(--glass-border);
        border-radius: 18px;
        padding: 2.25rem;
        margin: 1rem 0;
        box-shadow: 
            var(--shadow-md),
            inset 0 1px 0 rgba(255, 255, 255, 0.05),
            0 0 60px rgba(0, 0, 0, 0.3);
        transition: all var(--transition-slow) cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    /* Animated rainbow top border */
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(
            90deg,
            var(--primary),
            var(--cyan),
            var(--success),
            var(--pink),
            var(--purple)
        );
        background-size: 400% 100%;
        animation: rainbowFlow 8s linear infinite;
        opacity: 0;
        transition: opacity var(--transition-base);
        border-radius: 18px 18px 0 0;
    }
    
    @keyframes rainbowFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 400% 50%; }
    }
    
    /* Expanding glow circle on hover */
    .metric-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(74, 158, 255, 0.3) 0%, transparent 70%);
        transform: translate(-50%, -50%);
        transition: width 0.8s ease, height 0.8s ease;
        pointer-events: none;
    }
    
    .metric-card:hover {
        border-color: var(--primary);
        box-shadow: 
            var(--shadow-lg),
            0 0 50px rgba(74, 158, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            inset 0 0 80px rgba(74, 158, 255, 0.08);
        transform: translateY(-10px) scale(1.02);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card:hover::after {
        width: 600px;
        height: 600px;
    }
    
    .metric-title {
        color: var(--text-secondary);
        font-size: 0.8125rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        text-shadow: 0 0 10px rgba(74, 158, 255, 0.2);
        position: relative;
        z-index: 1;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2.75rem;
        font-weight: 900;
        margin-bottom: 0.75rem;
        background: linear-gradient(
            135deg,
            var(--primary) 0%,
            var(--cyan) 40%,
            var(--success) 70%,
            var(--yellow) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        background-size: 300% 300%;
        animation: gradientShimmer 6s ease infinite;
        letter-spacing: -0.03em;
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        text-shadow: 0 0 40px rgba(74, 158, 255, 0.6);
        filter: drop-shadow(0 0 30px rgba(74, 158, 255, 0.4));
        position: relative;
        z-index: 1;
    }
    
    @keyframes gradientShimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .metric-delta {
        color: var(--success);
        font-size: 0.9375rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4375rem 1rem;
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.2), rgba(0, 245, 160, 0.2));
        border-radius: 24px;
        border: 1px solid rgba(0, 214, 143, 0.4);
        box-shadow: 
            0 0 20px rgba(0, 214, 143, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        z-index: 1;
        transition: all var(--transition-base);
    }
    
    .metric-delta:hover {
        transform: scale(1.05);
        box-shadow: 
            0 0 30px rgba(0, 214, 143, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    .metric-delta.negative {
        color: var(--danger);
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.2), rgba(255, 107, 107, 0.2));
        border-color: rgba(255, 82, 82, 0.4);
        box-shadow: 
            0 0 20px rgba(255, 82, 82, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .metric-delta.negative:hover {
        box-shadow: 
            0 0 30px rgba(255, 82, 82, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    .metric-delta::before {
        content: '↗';
        font-size: 1.25rem;
        font-weight: 900;
        animation: arrowBounce 2s ease infinite;
    }
    
    .metric-delta.negative::before {
        content: '↘';
    }
    
    @keyframes arrowBounce {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-4px) rotate(5deg); }
    }
    
    /* Additional metric card variants */
    .metric-card.metric-card-primary {
        border-color: var(--primary-dim);
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.08), rgba(0, 212, 255, 0.08));
    }
    
    .metric-card.metric-card-success {
        border-color: var(--success-dim);
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.08), rgba(0, 245, 160, 0.08));
    }
    
    .metric-card.metric-card-warning {
        border-color: var(--warning-dim);
        background: linear-gradient(135deg, rgba(255, 171, 0, 0.08), rgba(255, 193, 7, 0.08));
    }
    
    .metric-card.metric-card-danger {
        border-color: var(--danger-dim);
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.08), rgba(255, 107, 107, 0.08));
    }
    
    /* =====================================================
       HEADERS - NEON GRADIENT TEXT WITH GLOW
       ===================================================== */
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(
            135deg,
            var(--primary) 0%,
            var(--cyan) 25%,
            var(--success) 50%,
            var(--pink) 75%,
            var(--purple) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        background-size: 300% 300%;
        animation: headerGradient 10s ease infinite, fadeInDown 0.6s ease;
        letter-spacing: -0.04em;
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        text-shadow: 
            0 0 50px rgba(74, 158, 255, 0.6),
            0 0 100px rgba(74, 158, 255, 0.4);
        filter: drop-shadow(0 0 40px rgba(74, 158, 255, 0.5));
        margin-bottom: 1rem;
    }
    
    @keyframes headerGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .sub-header {
        color: var(--text-secondary);
        font-size: 1.1875rem;
        margin-bottom: 2.5rem;
        font-weight: 500;
        animation: fadeInUp 0.6s ease;
        line-height: 1.7;
        text-shadow: 0 0 20px rgba(74, 158, 255, 0.2);
    }
    
    h1 {
        color: var(--text-primary);
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        text-shadow: 0 0 30px rgba(74, 158, 255, 0.3);
    }
    
    h2 {
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        text-shadow: 0 0 20px rgba(74, 158, 255, 0.2);
    }
    
    h3 {
        color: var(--text-primary);
        font-size: 1.375rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        text-shadow: 0 0 15px rgba(74, 158, 255, 0.2);
    }
    
    h4 {
        color: var(--text-bright);
        font-size: 1.125rem;
        font-weight: 600;
    }
    
    /* =====================================================
       TABS - CYBER PILL STYLE
       ===================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.75rem;
        background: var(--dark-tertiary);
        border-radius: 14px;
        padding: 0.625rem;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-radius: 10px;
        color: var(--text-secondary);
        padding: 0.875rem 1.75rem;
        font-weight: 700;
        font-size: 0.9375rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        transition: all var(--transition-base) cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, var(--primary-dim), var(--cyan));
        opacity: 0;
        transition: opacity var(--transition-base);
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary-light);
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        opacity: 0.2;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.25), rgba(0, 212, 255, 0.25));
        color: var(--cyan);
        box-shadow: 
            0 0 30px rgba(74, 158, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            inset 0 0 40px rgba(74, 158, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"]::before {
        opacity: 1;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 2rem;
    }
    
    /* =====================================================
       EXPANDER - CYBER ACCORDION
       ===================================================== */
    .streamlit-expanderHeader {
        background: var(--glass-bg-light);
        border: 1px solid var(--border);
        border-radius: 14px;
        color: var(--text-primary);
        font-weight: 700;
        padding: 1.25rem 1.75rem;
        transition: all var(--transition-base) ease;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .streamlit-expanderHeader::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, var(--primary-dim), transparent);
        transform: translateX(-100%);
        transition: transform 0.8s ease;
    }
    
    .streamlit-expanderHeader:hover::before {
        transform: translateX(100%);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--dark-tertiary);
        border-color: var(--primary);
        box-shadow: 
            0 0 30px rgba(74, 158, 255, 0.3),
            inset 0 0 40px rgba(74, 158, 255, 0.08);
        transform: translateX(6px);
    }
    
    .streamlit-expanderContent {
        background: var(--dark-card);
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 14px 14px;
        padding: 1.75rem;
        box-shadow: var(--shadow);
    }
    
    /* =====================================================
       ALERTS & MESSAGES - NEON STYLE
       ===================================================== */
    .alert {
        border-radius: 14px;
        padding: 1.25rem 1.75rem;
        margin: 1.5rem 0;
        border-left: 4px solid;
        animation: slideInRight 0.4s ease;
        box-shadow: var(--shadow);
        display: flex;
        align-items: center;
        gap: 1.25rem;
        position: relative;
        overflow: hidden;
    }
    
    .alert::before {
        font-size: 1.75rem;
        flex-shrink: 0;
        animation: pulse 2s ease infinite;
    }
    
    .alert::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transform: translateX(-100%);
        animation: alertShine 3s ease infinite;
    }
    
    @keyframes alertShine {
        0% { transform: translateX(-100%); }
        50%, 100% { transform: translateX(100%); }
    }
    
    .alert-success {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.18), rgba(0, 245, 160, 0.08));
        border-left-color: var(--success);
        color: var(--success-light);
        box-shadow: 0 0 40px rgba(0, 214, 143, 0.3);
    }
    
    .alert-success::before {
        content: '✓';
        color: var(--success);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 171, 0, 0.18), rgba(255, 193, 7, 0.08));
        border-left-color: var(--warning);
        color: var(--warning-light);
        box-shadow: 0 0 40px rgba(255, 171, 0, 0.3);
    }
    
    .alert-warning::before {
        content: '⚠';
        color: var(--warning);
    }
    
    .alert-error {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.18), rgba(255, 107, 107, 0.08));
        border-left-color: var(--danger);
        color: var(--danger-light);
        box-shadow: 0 0 40px rgba(255, 82, 82, 0.3);
    }
    
    .alert-error::before {
        content: '✕';
        color: var(--danger);
    }
    
    .alert-info {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.18), rgba(96, 176, 255, 0.08));
        border-left-color: var(--info);
        color: var(--primary-light);
        box-shadow: 0 0 40px rgba(74, 158, 255, 0.3);
    }
    
    .alert-info::before {
        content: 'ℹ';
        color: var(--info);
    }
    
    /* Streamlit native alerts */
    .stAlert {
        border-radius: 14px;
        border: none;
        box-shadow: var(--shadow);
        padding: 1.125rem 1.5rem;
    }
    
    /* =====================================================
       FILE UPLOADER - CYBER DRAG & DROP
       ===================================================== */
    [data-testid="stFileUploader"] {
        background: var(--glass-bg);
        border: 2px dashed var(--primary);
        border-radius: 18px;
        padding: 3rem;
        transition: all var(--transition-base) ease;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stFileUploader"]::before {
        content: '';
        position: absolute;
        inset: -2px;
        background: linear-gradient(45deg, var(--primary), var(--cyan), var(--pink), var(--purple));
        background-size: 400% 400%;
        border-radius: 20px;
        z-index: -1;
        opacity: 0;
        animation: borderFlow 4s ease infinite;
        transition: opacity var(--transition-base);
    }
    
    @keyframes borderFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--cyan);
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.08), rgba(0, 212, 255, 0.08));
        box-shadow: 
            0 0 50px rgba(74, 158, 255, 0.4),
            inset 0 0 60px rgba(74, 158, 255, 0.08);
        transform: scale(1.01);
    }
    
    [data-testid="stFileUploader"]:hover::before {
        opacity: 0.3;
    }
    
    [data-testid="stFileUploader"] section {
        border: none;
        background-color: transparent;
    }
    
    [data-testid="stFileUploader"] button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.75rem;
        font-weight: 700;
        transition: all var(--transition-base) ease;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background: var(--primary-light);
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(74, 158, 255, 0.5);
    }
    
    /* =====================================================
       PROGRESS BAR - NEON ANIMATED
       ===================================================== */
    .stProgress > div > div > div > div {
        background: linear-gradient(
            90deg,
            var(--primary) 0%,
            var(--cyan) 25%,
            var(--success) 50%,
            var(--pink) 75%,
            var(--primary) 100%
        );
        background-size: 300% 100%;
        border-radius: 12px;
        height: 12px;
        animation: progressFlow 3s ease infinite;
        box-shadow: 
            0 0 30px rgba(74, 158, 255, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stProgress > div > div > div > div::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: progressShimmer 1.5s ease infinite;
    }
    
    @keyframes progressFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }
    
    @keyframes progressShimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .stProgress > div > div {
        background: var(--dark-tertiary);
        border-radius: 12px;
        height: 12px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4);
        overflow: hidden;
    }
    
    /* =====================================================
       DATAFRAME & TABLES - CYBER GRID
       ===================================================== */
    [data-testid="stDataFrame"] {
        background: var(--dark-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: var(--shadow);
    }
    
    .stDataFrame table {
        background-color: var(--dark-card);
        color: var(--text-primary);
    }
    
    .stDataFrame thead tr {
        background: linear-gradient(135deg, var(--dark-elevated), var(--dark-quaternary));
        border-bottom: 2px solid var(--primary);
    }
    
    .stDataFrame thead th {
        color: var(--text-bright);
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.8125rem;
        letter-spacing: 0.08em;
        padding: 1.125rem 1.25rem;
        text-shadow: 0 0 10px rgba(74, 158, 255, 0.3);
    }
    
    .stDataFrame tbody td {
        padding: 1rem 1.25rem;
        border-bottom: 1px solid var(--border);
    }
    
    .stDataFrame tbody tr {
        transition: all var(--transition-fast) ease;
    }
    
    .stDataFrame tbody tr:hover {
        background: linear-gradient(90deg, rgba(74, 158, 255, 0.12), transparent);
        box-shadow: inset 3px 0 0 var(--primary);
    }
    
    .stDataFrame tbody tr:last-child td {
        border-bottom: none;
    }
    
    /* =====================================================
       METRICS (st.metric) - ENHANCED NEON
       ===================================================== */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 900;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        text-shadow: 0 0 30px rgba(74, 158, 255, 0.4);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary);
        text-transform: uppercase;
        font-size: 0.8125rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
        text-shadow: 0 0 10px rgba(74, 158, 255, 0.2);
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 800;
        font-size: 1rem;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        display: inline-block;
        box-shadow: var(--glow-sm);
    }
    
    [data-testid="stMetricDelta"] svg {
        fill: var(--success);
        filter: drop-shadow(0 0 8px var(--success-glow));
    }
    
    [data-testid="stMetricDelta"]:not([data-negative="true"]) {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.2), rgba(0, 245, 160, 0.2));
        color: var(--success-light);
        border: 1px solid rgba(0, 214, 143, 0.4);
    }
    
    [data-testid="stMetricDelta"][data-negative="true"] {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.2), rgba(255, 107, 107, 0.2));
        color: var(--danger-light);
        border: 1px solid rgba(255, 82, 82, 0.4);
    }
    
    [data-testid="stMetricDelta"][data-negative="true"] svg {
        fill: var(--danger);
        filter: drop-shadow(0 0 8px var(--danger-glow));
    }
    
    /* =====================================================
       SCROLLBAR - NEON GLOW
       ===================================================== */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--dark-secondary);
        border-radius: 12px;
        box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary), var(--cyan), var(--success));
        background-size: 200% 200%;
        border-radius: 12px;
        border: 2px solid var(--dark-secondary);
        box-shadow: 0 0 15px rgba(74, 158, 255, 0.6);
        animation: scrollbarGradient 3s ease infinite;
    }
    
    @keyframes scrollbarGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-light), #00e5ff, var(--success-light));
        box-shadow: 0 0 25px rgba(74, 158, 255, 0.8);
    }
    
    ::-webkit-scrollbar-corner {
        background: var(--dark-secondary);
    }
    
    /* =====================================================
       SPINNER & LOADING
       ===================================================== */
    .stSpinner > div {
        border-top-color: var(--primary);
        border-right-color: var(--cyan);
        border-bottom-color: var(--success);
        border-left-color: var(--pink);
        animation: spin 0.8s linear infinite, colorShift 2s ease infinite;
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.5);
    }
    
    @keyframes colorShift {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(180deg); }
    }
    
    /* =====================================================
       CODE BLOCKS - TERMINAL STYLE
       ===================================================== */
    code {
        background: linear-gradient(135deg, var(--dark-tertiary), var(--dark-quaternary));
        color: var(--cyan);
        padding: 0.375rem 0.625rem;
        border-radius: 8px;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.875em;
        font-weight: 500;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 
            0 0 15px rgba(0, 212, 255, 0.2),
            inset 0 0 20px rgba(0, 212, 255, 0.05);
        text-shadow: 0 0 8px rgba(0, 212, 255, 0.5);
    }
    
    pre {
        background: var(--dark-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.5rem;
        overflow-x: auto;
        box-shadow: 
            var(--shadow),
            inset 0 0 40px rgba(0, 0, 0, 0.3);
        position: relative;
    }
    
    pre::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, var(--primary), var(--cyan), var(--success));
        background-size: 200% 100%;
        animation: codeHeader 3s linear infinite;
    }
    
    @keyframes codeHeader {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    pre code {
        background: transparent;
        border: none;
        padding: 0;
        box-shadow: none;
    }
    
    /* =====================================================
       RADIO & CHECKBOX - NEON STYLED
       ===================================================== */
    .stRadio > div,
    .stCheckbox > div {
        color: var(--text-primary);
    }
    
    .stRadio label,
    .stCheckbox label {
        transition: all var(--transition-fast) ease;
        border-radius: 10px;
        padding: 0.625rem 1rem;
        font-weight: 500;
        cursor: pointer;
    }
    
    .stRadio label:hover,
    .stCheckbox label:hover {
        background: rgba(74, 158, 255, 0.12);
        color: var(--primary-light);
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.2);
    }
    
    .stRadio input[type="radio"],
    .stCheckbox input[type="checkbox"] {
        accent-color: var(--primary);
        width: 20px;
        height: 20px;
        cursor: pointer;
    }
    
    /* =====================================================
       SELECT & MULTISELECT
       ===================================================== */
    .stSelectbox label,
    .stMultiSelect label {
        color: var(--text-bright);
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.8125rem;
        letter-spacing: 0.08em;
        text-shadow: 0 0 10px rgba(74, 158, 255, 0.2);
    }
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--dark-tertiary);
        border: 2px solid var(--border);
        border-radius: 12px;
        transition: all var(--transition-base) ease;
    }
    
    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(74, 158, 255, 0.15);
    }
    
    /* =====================================================
       SLIDER - NEON TRACK
       ===================================================== */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--cyan), var(--success));
        background-size: 200% 100%;
        border-radius: 12px;
        animation: sliderGradient 3s ease infinite;
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.5);
    }
    
    @keyframes sliderGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .stSlider > div > div > div {
        background: var(--dark-tertiary);
        border-radius: 12px;
        height: 10px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4);
    }
    
    .stSlider [role="slider"] {
        background: var(--glass-bg-light);
        border: 3px solid var(--primary);
        box-shadow: 
            0 0 20px rgba(74, 158, 255, 0.6),
            inset 0 0 10px rgba(74, 158, 255, 0.2);
        width: 24px;
        height: 24px;
        transition: all var(--transition-base) ease;
    }
    
    .stSlider [role="slider"]:hover {
        box-shadow: 
            0 0 30px rgba(74, 158, 255, 0.8),
            inset 0 0 15px rgba(74, 158, 255, 0.3);
        transform: scale(1.15);
    }
    
    /* =====================================================
       LOGIN FORM - CYBER GLASSMORPHISM
       ===================================================== */
    .login-container {
        max-width: 500px;
        margin: 4rem auto;
        padding: 3.5rem;
        background: var(--glass-bg-light);
        border: 1px solid var(--glass-border);
        border-radius: 28px;
        box-shadow: 
            var(--shadow-2xl),
            0 0 80px rgba(74, 158, 255, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: fadeInUp 0.6s ease;
        position: relative;
        overflow: hidden;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        inset: -3px;
        background: linear-gradient(135deg, var(--primary), var(--cyan), var(--pink), var(--purple));
        background-size: 400% 400%;
        border-radius: 30px;
        z-index: -1;
        opacity: 0.4;
        filter: blur(30px);
        animation: loginBorderGlow 8s ease infinite;
    }
    
    @keyframes loginBorderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .login-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: loginShimmer 3s ease infinite;
    }
    
    @keyframes loginShimmer {
        0% { left: -100%; }
        50%, 100% { left: 100%; }
    }
    
    .login-logo {
        text-align: center;
        font-size: 5rem;
        margin-bottom: 1.75rem;
        animation: logoFloat 3s ease-in-out infinite, logoPulse 2s ease infinite;
        filter: drop-shadow(0 0 40px rgba(74, 158, 255, 0.8));
        position: relative;
        z-index: 1;
    }
    
    @keyframes logoFloat {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
    }
    
    @keyframes logoPulse {
        0%, 100% { 
            filter: drop-shadow(0 0 40px rgba(74, 158, 255, 0.8)); 
        }
        50% { 
            filter: drop-shadow(0 0 60px rgba(74, 158, 255, 1)); 
        }
    }
    
    .login-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary), var(--cyan), var(--success));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% 200%;
        animation: loginTitleGradient 4s ease infinite;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
        font-family: 'Space Grotesk', sans-serif;
        text-shadow: 0 0 40px rgba(74, 158, 255, 0.6);
        filter: drop-shadow(0 0 30px rgba(74, 158, 255, 0.5));
        position: relative;
        z-index: 1;
    }
    
    @keyframes loginTitleGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .login-subtitle {
        text-align: center;
        color: var(--text-secondary);
        margin-bottom: 3rem;
        font-size: 1.0625rem;
        font-weight: 500;
        text-shadow: 0 0 15px rgba(74, 158, 255, 0.2);
        position: relative;
        z-index: 1;
    }
    
    /* =====================================================
       BADGES & TAGS
       ===================================================== */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4375rem 1rem;
        border-radius: 24px;
        font-size: 0.8125rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        box-shadow: var(--glow-sm);
        transition: all var(--transition-base) ease;
    }
    
    .badge:hover {
        transform: scale(1.05);
        box-shadow: var(--glow-md);
    }
    
    .badge-success {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.2), rgba(0, 245, 160, 0.2));
        color: var(--success-light);
        border: 1px solid rgba(0, 214, 143, 0.4);
    }
    
    .badge-warning {
        background: linear-gradient(135deg, rgba(255, 171, 0, 0.2), rgba(255, 193, 7, 0.2));
        color: var(--warning-light);
        border: 1px solid rgba(255, 171, 0, 0.4);
    }
    
    .badge-danger {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.2), rgba(255, 107, 107, 0.2));
        color: var(--danger-light);
        border: 1px solid rgba(255, 82, 82, 0.4);
    }
    
    .badge-info {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.2), rgba(96, 176, 255, 0.2));
        color: var(--primary-light);
        border: 1px solid rgba(74, 158, 255, 0.4);
    }
    
    .badge-primary {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.25), rgba(0, 212, 255, 0.25));
        color: var(--cyan);
        border: 1px solid rgba(74, 158, 255, 0.5);
    }
    
    /* =====================================================
       ANIMATIONS
       ===================================================== */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(40px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-40px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes glow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(74, 158, 255, 0.6)); }
        50% { filter: drop-shadow(0 0 40px rgba(74, 158, 255, 0.9)); }
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
    .font-black { font-weight: 900; }
    
    .text-xs { font-size: 0.75rem; }
    .text-sm { font-size: 0.875rem; }
    .text-base { font-size: 1rem; }
    .text-lg { font-size: 1.125rem; }
    .text-xl { font-size: 1.25rem; }
    .text-2xl { font-size: 1.5rem; }
    .text-3xl { font-size: 1.875rem; }
    
    .mt-1 { margin-top: 0.5rem; }
    .mt-2 { margin-top: 1rem; }
    .mt-3 { margin-top: 1.5rem; }
    .mt-4 { margin-top: 2rem; }
    .mt-5 { margin-top: 2.5rem; }
    .mt-6 { margin-top: 3rem; }
    
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    .mb-3 { margin-bottom: 1.5rem; }
    .mb-4 { margin-bottom: 2rem; }
    .mb-5 { margin-bottom: 2.5rem; }
    .mb-6 { margin-bottom: 3rem; }
    
    .p-1 { padding: 0.5rem; }
    .p-2 { padding: 1rem; }
    .p-3 { padding: 1.5rem; }
    .p-4 { padding: 2rem; }
    .p-5 { padding: 2.5rem; }
    .p-6 { padding: 3rem; }
    
    .rounded { border-radius: 8px; }
    .rounded-lg { border-radius: 12px; }
    .rounded-xl { border-radius: 16px; }
    .rounded-2xl { border-radius: 20px; }
    .rounded-3xl { border-radius: 24px; }
    .rounded-full { border-radius: 9999px; }
    
    .shadow-xs { box-shadow: var(--shadow-xs); }
    .shadow-sm { box-shadow: var(--shadow-sm); }
    .shadow { box-shadow: var(--shadow); }
    .shadow-md { box-shadow: var(--shadow-md); }
    .shadow-lg { box-shadow: var(--shadow-lg); }
    .shadow-xl { box-shadow: var(--shadow-xl); }
    .shadow-2xl { box-shadow: var(--shadow-2xl); }
    
    .glow-xs { box-shadow: var(--glow-xs); }
    .glow-sm { box-shadow: var(--glow-sm); }
    .glow-md { box-shadow: var(--glow-md); }
    .glow-lg { box-shadow: var(--glow-lg); }
    .glow-xl { box-shadow: var(--glow-xl); }
    
    /* =====================================================
       RESPONSIVE DESIGN
       ===================================================== */
    @media (max-width: 1024px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .metric-value {
            font-size: 2.25rem;
        }
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .sub-header {
            font-size: 1rem;
        }
        
        .metric-value {
            font-size: 1.875rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .login-container {
            margin: 2rem 1rem;
            padding: 2.5rem;
        }
        
        .login-logo {
            font-size: 4rem;
        }
        
        .login-title {
            font-size: 2rem;
        }
        
        .stButton > button {
            padding: 0.625rem 1.75rem;
            font-size: 0.875rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.75rem;
        }
        
        .sub-header {
            font-size: 0.9375rem;
        }
        
        .metric-card {
            padding: 1.25rem;
        }
        
        .metric-value {
            font-size: 1.625rem;
        }
        
        .login-container {
            padding: 2rem;
        }
        
        .login-logo {
            font-size: 3.5rem;
        }
        
        .login-title {
            font-size: 1.75rem;
        }
        
        [data-testid="stSidebar"] label {
            padding: 0.625rem 1rem;
        }
    }
    
    /* =====================================================
       PERFORMANCE OPTIMIZATIONS
       ===================================================== */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* SIDEBAR FIX - CRITICAL */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    left: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    z-index: 999999 !important;
    background: rgba(30, 41, 59, 0.95) !important;
    border-radius: 0 12px 12px 0 !important;
    padding: 0.75rem !important;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5) !important;
}

[data-testid="collapsedControl"]:hover {
    background: rgba(74, 158, 255, 0.2) !important;
    transform: translateY(-50%) scale(1.1) !important;
}

[data-testid="collapsedControl"] svg {
    fill: #e2e8f0 !important;
    width: 20px !important;
    height: 20px !important;
}
</style>
"""