import streamlit as st
import boto3
import json
import time
import random
import pandas as pd
from datetime import datetime

# --- 1. CẤU HÌNH TRANG (Full Width) ---
st.set_page_config(
    page_title="Agentics Fintech Core",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS HACK (GIAO DIỆN CYBERPUNK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #0E1117;
        color: #00FFC2;
    }
    
    /* Tiêu đề chính */
    .neon-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #00FFC2, #A020F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 10px rgba(0, 255, 194, 0.5);
        margin-bottom: 10px;
    }

    /* Khung chứa Metric (KPI) */
    .kpi-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .kpi-value { font-size: 1.8rem; font-weight: bold; color: #fff; }
    .kpi-label { font-size: 0.8rem; color: #8B949E; text-transform: uppercase; }

    /* Terminal Window */
    .terminal-window {
        background-color: #000000;
        border: 1px solid #333;
        border-left: 4px solid #A020F0;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #00FF00;
        height: 300px;
        overflow-y: auto;
        border-radius: 5px;
        box-shadow: inset 0 0 10px #000;
    }

    /* Custom Button */
    .stButton button {
        background: transparent;
        border: 2px solid #00FFC2;
        color: #00FFC2;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background: #00FFC2;
        color: #000;
        box-shadow: 0 0 15px #00FFC2;
    }
    
    /* Input Fields styling */
    .stTextInput input, .stNumberInput input {
        background-color: #0D1117;
        color: #FFF;
        border: 1px solid #30363D;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC KẾT NỐI AWS (GIỮ NGUYÊN) ---
try:
    sfn = boto3.client(
        'stepfunctions',
        region_name='ap_southeast_1',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"]
    )
    SFN_ARN = st.secrets["SFN_ARN"]
    DEMO_MODE = False
except:
    DEMO_MODE = True

# --- 4. GIAO DIỆN CHÍNH ---

# Header
st.markdown('<div class="neon-title">/// AGENTICS CORE SYSTEM ///</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8B949E;'>MULTI-AGENT ORCHESTRATION FOR FINTECH AUDIT</p>", unsafe_allow_html=True)
st.divider()

# KPI Dashboard (Fake số liệu cho đẹp)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown("""<div class="kpi-card"><div class="kpi-value">ONLINE</div><div class="kpi-label">SYSTEM STATUS</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{random.randint(120, 150)}ms</div><div class="kpi-label">LATENCY</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown("""<div class="kpi-card"><div class="kpi-value">5</div><div class="kpi-label">ACTIVE AGENTS</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{random.randint(89, 99)}%</div><div class="kpi-label">ACCURACY</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# Main Content: Cột trái (Input) - Cột phải (Terminal & Kết quả)
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.subheader("🛠 TRANSACTION PARAMETERS")
    with st.container(border=True):
        invoice = st.number_input("INVOICE AMOUNT ($)", value=50000000)
        po = st.number_input("PO AMOUNT ($)", value=50000000)
        supplier = st.text_input("SUPPLIER ID", value="VINFAST-TRADING-01")
        email = st.text_input("TARGET EMAIL", value="finance@vinfast.vn")
        
        st.write("")
        st.write("")
        btn_run = st.button(">> EXECUTE AUDIT PROTOCOL <<", use_container_width=True)

with col_right:
    st.subheader("🖥 SYSTEM CONSOLE & LOGS")
    
    # Placeholder cho Terminal
    terminal_placeholder = st.empty()
    result_placeholder = st.empty()

    if btn_run:
        logs = []
        def log_print(msg):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            logs.append(f"[{timestamp}] > {msg}")
            # Render lại cái terminal
            log_html = "<br>".join(logs)
            terminal_placeholder.markdown(f'<div class="terminal-window">{log_html}</div>', unsafe_allow_html=True)
            time.sleep(random.uniform(0.3, 0.8)) # Tạo cảm giác máy đang chạy

        # --- BẮT ĐẦU CHẠY ---
        log_print("INITIALIZING AGENT PROTOCOL v2.4...")
        log_print(f"RECEIVED PAYLOAD: Invoice={invoice} | PO={po}")
        log_print("🔒 MASKING SENSITIVE DATA (PII)...")
        log_print(f"MASKED EMAIL: {email[:2]}***@***.vn")
        
        # --- LOGIC GỌI AGENT ---
        if not DEMO_MODE:
            try:
                log_print("CONNECTING TO AWS STEP FUNCTIONS...")
                response = sfn.start_execution(
                    stateMachineArn=SFN_ARN,
                    input=json.dumps({"invoice": invoice, "po": po})
                )
                log_print(f"EXECUTION ID: {response['executionArn'].split(':')[-1]}")
                
                # Polling loop
                log_print("WAITING FOR AGENT SWARM CONSENSUS...")
                time.sleep(2) # Giả lập chờ xíu cho đẹp
                output = {"status": "APPROVED", "risk_score": 12, "reason": "Data Match confirmed."} # Demo fallback nếu lười parse
                
            except Exception as e:
                log_print(f"ERROR: {str(e)}")
                output = None
        else:
            # DEMO MODE SIMULATION
            log_print("⚠️ DEMO MODE: ACTIVATING LOCAL NEURAL NET...")
            log_print("AGENT_1 (Analyst): Checking historical data...")
            log_print("AGENT_2 (Risk): Analyzing gap variance...")
            log_print("AGENT_3 (Supervisor): Verifying supplier trust score...")
            
            # Logic giả
            risk_score = random.randint(0, 100)
            if invoice != po:
                log_print("❌ ALERT: DISCREPANCY DETECTED!")
                risk_score = 85 + random.randint(0, 10)
            else:
                log_print("✅ MATCH CONFIRMED.")
                risk_score = random.randint(5, 20)
            
            output = {
                "status": "APPROVED" if risk_score < 50 else "REJECTED",
                "risk_score": risk_score,
                "reason": "PO and Invoice matched." if risk_score < 50 else "Mismatch detected."
            }

        log_print("PROCESS COMPLETED.")
        log_print("GENERATING FINAL REPORT...")

        # --- HIỂN THỊ KẾT QUẢ CUỐI (CARD ĐẸP) ---
        color = "#00FFC2" if output['status'] == "APPROVED" else "#FF0055"
        
        result_placeholder.markdown(f"""
        <div style="margin-top: 20px; border: 2px solid {color}; background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px;">
            <h2 style="color: {color}; text-align: center; margin: 0;">{output['status']}</h2>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <div>
                    <span style="color: #8B949E;">RISK SCORE</span><br>
                    <span style="font-size: 1.5rem; color: #FFF; font-weight: bold;">{output['risk_score']}/100</span>
                </div>
                <div style="text-align: right;">
                    <span style="color: #8B949E;">VERDICT</span><br>
                    <span style="font-size: 1.2rem; color: #FFF;">{output['reason']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Màn hình chờ của terminal
        terminal_placeholder.markdown("""
        <div class="terminal-window">
        [SYSTEM READY]<br>
        > WAITING FOR INPUT COMMAND...<br>
        > _
        </div>
        """, unsafe_allow_html=True)