import time
import sys

def simulate_reply():
    # 1. Giả lập nhận tin nhắn
    print("\n💬 [Slack Incoming from @CEO]: 'Agent 5, tại sao giao dịch TX_1020 lại bị gắn cờ rủi ro thế?'")
    print("...")
    time.sleep(1.5) 
    
    print("... 🔍 Agent 5 đang truy xuất Audit Log từ Agent 4 ...")
    time.sleep(1.5)
    
    # 2. Bot trả lời và hỏi ý kiến
    reply = """
    🤖 **Agent 5 trả lời:** Dạ, em đã kiểm tra chéo dữ liệu ạ.
    ----------------------------------------
    - 📦 **Giao dịch:** TX_1020
    - 💰 **Số tiền:** 200,000,000 VND
    - 🚩 **Lý do gắn cờ:** 1. Số tiền vượt ngưỡng trung bình ngày.
        2. IP đến từ vùng lạ (Nigeria).
    
    👉 **Hành động:** Em đã tạm khoá giao dịch này. Sếp muốn [DUYET] hay [HUY] ạ?
    """
    print(reply)

    # 3. PHẦN MỚI: Cho phép bạn gõ câu trả lời thật!
    action = input(">> ⌨️  Sếp nhập lệnh (Gõ 'HUY' hoặc 'DUYET' rồi Enter): ")

    print("\n...")
    time.sleep(1)
    
    if "HUY" in action.upper():
        print("✅ **Agent 5:** Đã nhận lệnh HUỶ. Giao dịch TX_1020 đã bị từ chối và báo cáo lên hệ thống Audit.")
    elif "DUYET" in action.upper():
        print("⚠️ **Agent 5:** Đã nhận lệnh DUYỆT. (Cảnh báo: Sếp chịu trách nhiệm rủi ro cho giao dịch này).")
    else:
        print("🤖 **Agent 5:** Em không hiểu lệnh. Đã giữ nguyên trạng thái khoá.")

if __name__ == "__main__":
    simulate_reply()