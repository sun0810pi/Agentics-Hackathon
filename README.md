# 🚀 AUDIT CORE V4 PRO - WEB APP

## Kiến trúc hệ thống

```
┌─────────────────────┐
│   Web App (Browser) │
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────┐
│  FastAPI Backend    │◄──── Slack/Telegram/Zalo
└──────────┬──────────┘
           │
    Agent 1 → Agent 2 → Agent 3
           │
      Excel/CSV/AI
```

## 📦 Thành phần

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI |
| Agents | Python |
| Web UI | HTML + JS |
| Charts | Chart.js |
| Storage | In-Memory (có thể thay DynamoDB) |
| Notify | Slack/Telegram/Zalo webhooks |

---

## 🎯 3 Agents Workflow

### **AGENT 1 - Ingestion & Sanitization**
- ✅ Validate payload
- ✅ Mask PII (email, bank account)
- ✅ Tokenize dữ liệu nhạy cảm
- ✅ Normalize schema
- **Output**: Canonical JSON

### **AGENT 2 - Matching (Pandas)**
- ✅ Load DataFrame
- ✅ Invoice vs PO comparison
- ✅ Calculate diff (abs, %)
- ✅ Label: MATCH / MISMATCH
- ✅ Risk: LOW / MEDIUM / HIGH

### **AGENT 3 - AI Analysis + Human-in-Loop**
- ✅ Phân tích AI (Gemini/Claude API)
- ✅ Generate verdict
- ✅ Confidence scoring
- ✅ Quyết định: Auto-approve hoặc Human review

---

## 🚀 Cài đặt & Chạy

### 1️⃣ Cài đặt dependencies

```bash
cd audit-webapp
pip install -r requirements.txt
```

### 2️⃣ Chạy Backend (FastAPI)

```bash
cd backend
python main.py
```

Backend sẽ chạy tại: **http://localhost:8000**

### 3️⃣ Truy cập Web App

Mở browser và truy cập:

```
http://localhost:8000
```

Giao diện web sẽ tự động load từ thư mục `frontend/`

---

## 📖 API Documentation

### **GET /health**
Health check

```json
{
  "status": "healthy",
  "agents": {
    "agent1": "active",
    "agent2": "active",
    "agent3": "active"
  }
}
```

### **POST /api/v1/process-batch**
Xử lý batch invoices

**Request:**
```json
{
  "items": [
    {
      "invoice_amount": 1000000,
      "po_amount": 950000,
      "supplier": "ABC Corp",
      "email": "contact@abc.com",
      "bank_account": "1234567890"
    }
  ]
}
```

**Response:**
```json
{
  "total_processed": 1,
  "success_count": 1,
  "failed_count": 0,
  "results": [...]
}
```

### **POST /api/v1/upload-excel**
Upload Excel file và tự động process

```bash
curl -X POST "http://localhost:8000/api/v1/upload-excel" \
  -F "file=@invoices.xlsx"
```

### **GET /api/v1/dashboard**
Lấy dashboard stats

```json
{
  "total_transactions": 100,
  "pending_review": 5,
  "approved": 90,
  "rejected": 5,
  "total_amount": 5000000000,
  "avg_processing_time": 0.5,
  "high_risk_count": 3
}
```

### **GET /api/v1/transactions**
Lấy tất cả transactions

### **GET /api/v1/transactions/{tx_id}**
Lấy 1 transaction

### **POST /api/v1/transactions/{tx_id}/approve**
Approve transaction

### **POST /api/v1/transactions/{tx_id}/reject?reason=...**
Reject transaction

---

## 🔌 Tích hợp Notifications

### Slack
```bash
curl -X POST "http://localhost:8000/api/v1/notify/slack" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "message": "🚨 High risk transaction detected!"
  }'
```

### Telegram
```bash
curl -X POST "http://localhost:8000/api/v1/notify/telegram" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "message": "⚠️ Transaction needs review"
  }'
```

---

## 🎨 Features

### ✅ Dashboard
- Real-time stats
- Status distribution chart
- Risk level breakdown
- Recent transactions table

### ✅ Upload Page
- Drag & drop Excel/CSV
- Smart column detection
- Auto-processing
- Progress feedback

### ✅ Transactions Page
- Filter by status
- Filter by risk level
- Human approval workflow
- Inline actions (Approve/Reject)

### ✅ Agent Monitor
- Real-time agent status
- Processed/Failed counters
- Task breakdown
- Status indicators (idle/active/error)

### ✅ Analytics
- Transaction timeline
- Top 10 suppliers by amount
- Advanced visualizations

---

## 🔧 Customization

### Thay đổi Risk Threshold
Trong `backend/agents.py`:

```python
class Agent2Matching:
    THRESHOLD_PERCENTAGE = 5.0  # Đổi thành 10.0 để nới lỏng
```

### Tích hợp AI thực (Claude/Gemini)
Trong `backend/agents.py`, method `Agent3AIAnalysis.analyze_with_ai()`:

```python
def analyze_with_ai(self, agent1_output, agent2_output):
    # THAY STUB NÀY BẰNG:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": "YOUR_API_KEY",
            "anthropic-version": "2023-06-01"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": f"Analyze this transaction: {agent1_output.dict()}"
            }]
        }
    )
    # ... parse response
```

### Thay In-Memory DB bằng DynamoDB
Trong `backend/database.py`:

```python
import boto3

class DynamoDBDatabase:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
        self.table = self.dynamodb.Table('audit-transactions')
    
    def save_transaction(self, record):
        self.table.put_item(Item=record.dict())
```

---

## 🎯 Roadmap (Next Steps)

### Phase 2: Windows Desktop App (Electron)
```
audit-webapp/
├── electron/
│   ├── main.js          # Electron main process
│   ├── preload.js       # Bridge giữa Electron & Web
│   └── package.json
```

**Setup Electron:**
```bash
npm install electron electron-builder
```

**main.js:**
```javascript
const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true
    }
  });
  
  win.loadURL('http://localhost:8000');
}

app.whenReady().then(createWindow);
```

**Package as .exe:**
```bash
npm run build  # Creates Windows installer
```

### Phase 3: Auto Excel Monitoring
Python worker đọc folder Excel tự động:

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ExcelWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.xlsx'):
            # Upload file to API
            with open(event.src_path, 'rb') as f:
                requests.post('http://localhost:8000/api/v1/upload-excel', 
                              files={'file': f})

observer = Observer()
observer.schedule(ExcelWatcher(), path='C:/Invoices', recursive=False)
observer.start()
```

---

## 📞 Support

Nếu gặp lỗi:

1. Check backend đang chạy: `curl http://localhost:8000/health`
2. Check browser console (F12)
3. Check backend logs

## 🎉 Demo Flow

1. **Start server**: `python backend/main.py`
2. **Truy cập**: http://localhost:8000
3. **Upload Excel** với cột:
   - Invoice Amount
   - PO Amount
   - Supplier
   - (Optional) Email, Bank Account
4. **Xem Dashboard** - Stats tự động update
5. **Check Transactions** - Filter, approve/reject
6. **Monitor Agents** - Xem agent đang làm gì

---

## 🔐 Security Notes

- **KHÔNG commit API keys** vào Git
- Dùng environment variables cho production
- Enable CORS properly cho production domain
- Thêm authentication layer (JWT tokens)
- Rate limiting cho API endpoints

---

**Made with 💎 by Audit Core Team**
