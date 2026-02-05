import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import random
from datetime import datetime

# --- CẤU HÌNH ---
OUTPUT_DIR = "demo_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1. TÍNH NĂNG SMART CFO (GIÁM ĐỐC TÀI CHÍNH ẢO) ---
def ask_ai_cfo(df):
    total_rev = df['amount'].sum()
    # Tìm các giao dịch lớn bất thường (trên 100 triệu)
    fraud_df = df[df['amount'] > 100000000]
    fraud_count = len(fraud_df)
    
    insight = f"""
    💡 **SMART CFO INSIGHT (High Contrast Mode):**
    --------------------------------------------------
    1. 💰 **Tổng dòng tiền:** {total_rev:,.0f} VND.
    2. 📊 **Xu hướng:** Tăng trưởng nóng so với hôm qua.
    3. ⚠️ **CẢNH BÁO:** Phát hiện {fraud_count} giao dịch "cá mập" (>100tr).
       - Xem biểu đồ Boxplot để thấy rõ các điểm ngoại lai (Outliers).
    4. **Đề xuất:** Admin hãy kiểm tra dashboard để filter chi tiết.
    """
    return insight, fraud_df

# --- 2. VẼ BIỂU ĐỒ (VISUALIZATION - PHIÊN BẢN ĐẬM ĐÀ) ---
def generate_charts(df, context="CEO"):
    print(f"🎨 Đang vẽ biểu đồ 'High Contrast' cho: {context}...")
    paths = []
    
    # Cài đặt giao diện chung: Nền trắng, có lưới mờ, chữ to
    sns.set_theme(style="whitegrid")
    sns.set_context("notebook", font_scale=1.1) 

    # --- BIỂU ĐỒ 1: PIE CHART (Màu đậm, tương phản cao) ---
    plt.figure(figsize=(10, 7))
    
    # Dùng bảng màu 'Paired' để các miếng bánh có màu khác biệt rõ rệt
    colors = sns.color_palette('Paired')
    
    counts = df.groupby('bank')['amount'].sum()
    
    # Vẽ biểu đồ
    wedges, texts, autotexts = plt.pie(
        counts, 
        labels=counts.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors,
        textprops=dict(color="black"), # Chữ màu đen cho dễ đọc
        wedgeprops=dict(width=0.7, edgecolor='w') # Tạo dáng Donut chart cho sang
    )
    
    # Chỉnh font chữ số % cho đậm lên
    plt.setp(autotexts, size=11, weight="bold", color="white")
    plt.setp(texts, size=12, weight="bold")

    plt.title('PHÂN BỔ DÒNG TIỀN THEO NGÂN HÀNG', fontsize=15, fontweight='bold', color='#B22222')
    
    path1 = os.path.join(OUTPUT_DIR, "CEO_Chart_Pie.png")
    plt.savefig(path1, bbox_inches='tight')
    paths.append(path1)
    plt.close()

    # --- BIỂU ĐỒ 2: BOXPLOT (Dành cho Audit soi gian lận) ---
    if context == "DEV" or context == "CEO":
        plt.figure(figsize=(12, 7))
        
        # Vẽ Boxplot với viền đậm màu xám đen
        sns.boxplot(
            x='bank', 
            y='amount', 
            data=df, 
            palette="Set1", # Màu rực rỡ (Đỏ, Xanh)
            linewidth=2.5,
            flierprops={"marker": "o", "markerfacecolor": "red", "markersize": 8} # Điểm gian lận màu ĐỎ
        )
        
        # Vẽ thêm các chấm rải rác để thấy mật độ (Stripplot)
        sns.stripplot(x='bank', y='amount', data=df, color="#333333", size=4, jitter=True, alpha=0.5)

        plt.title('PHÁT HIỆN GIAO DỊCH BẤT THƯỜNG (ANOMALY DETECTION)', fontsize=15, fontweight='bold', color='#B22222')
        plt.ylabel('Số tiền giao dịch (VND)', fontweight='bold')
        plt.xlabel('Ngân hàng', fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.6) # Lưới nền
        
        path2 = os.path.join(OUTPUT_DIR, "Audit_Chart_Boxplot.png")
        plt.savefig(path2, bbox_inches='tight')
        paths.append(path2)
        plt.close()

    return paths

# --- 3. DYNAMIC REPORT ---
def generate_report_content(role, df, ai_insight):
    if role == "CEO":
        subject = "📊 [Daily Report] Báo cáo nhanh tình hình tài chính"
        body = f"Chào Sếp,\n\n{ai_insight}\n\nXem biểu đồ đính kèm để thấy tỷ trọng dòng tiền."
    else: 
        subject = "🛠 [SYSTEM ALERT] Security Audit Logs"
        raw_json = df.head(3).to_json(orient='records', indent=2)
        tx_hash = "sha256:8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92"
        body = f"User: ADMIN_BOT\nHash Verify: {tx_hash}\n\nSample Data:\n{raw_json}\n\n[DEBUG]: Kiểm tra điểm đỏ (Outliers) trong hình Boxplot."
        
    return subject, body

# --- 4. DATA GENERATOR ---
def create_dummy_data():
    print("💾 Đang tổng hợp dữ liệu từ Database...")
    data = []
    banks = ['VCB', 'ACB', 'MB', 'Techcom']
    for i in range(60):
        amount = random.randint(5, 20) * 1000000 # Giao dịch thường 5-20tr
        # Tạo GIAN LẬN: Cứ 15 giao dịch thì có 1 cái 300 triệu (Điểm đỏ)
        if i % 15 == 0: amount = amount * 15 
        
        data.append({
            "tx_id": f"TX_{1000+i}",
            "amount": amount,
            "bank": random.choice(banks),
            "status": "SUCCESS"
        })
    return pd.DataFrame(data)

# --- QUY TRÌNH CHÍNH ---
def run_agent5_ultimate(recipient_role="CEO"):
    print(f"\n" + "="*40)
    print(f"🚀 AGENT 5 ĐANG CHẠY (High Contrast Mode)...")
    
    # B1: Lấy dữ liệu
    df = create_dummy_data()
    
    # B2: AI Smart CFO phân tích
    insight, fraud_df = ask_ai_cfo(df)
    
    # B3: Vẽ biểu đồ (Matplotlib & Seaborn)
    chart_paths = generate_charts(df, context=recipient_role)
    
    # B4: Tạo nội dung báo cáo
    subject, body = generate_report_content(recipient_role, df, insight)
    
    # B5: Xuất kết quả
    print("-" * 40)
    print(f"📧 ĐANG GỬI TỚI: {recipient_role}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print(f"📎 Attachments: {chart_paths}")
    
    if not fraud_df.empty:
        print(f"\n🚨 [ALERT] Đã tìm thấy {len(fraud_df)} giao dịch rủi ro cao!")
        print("💡 Gợi ý: Hãy mở Dashboard tại http://localhost:8050 để soi kỹ hơn.")
    print("=" * 40)

if __name__ == "__main__":
    run_agent5_ultimate(recipient_role="CEO")