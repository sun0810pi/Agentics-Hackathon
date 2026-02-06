# FILE: app/api/routes.py
from fastapi import APIRouter
from typing import List
from app.models.schemas import Transaction

router = APIRouter()

@router.post("/process-batch")
async def process_batch(transactions: List[Transaction]):
    """
    API nhận danh sách giao dịch từ Dashboard (Streamlit) gửi sang.
    """
    print(f"🔥 [API] Đã nhận {len(transactions)} dòng dữ liệu từ Dashboard")
    
    results = []
    
    # Giả lập xử lý từng dòng (Sau này nhét Agent vào đây)
    for idx, tx in enumerate(transactions):
        # Ví dụ: Logic so sánh đơn giản (Agent 2)
        diff = abs(tx.invoice_amount - tx.po_amount)
        status = "MATCH" if diff == 0 else "MISMATCH"
        
        results.append({
            "id": idx,
            "supplier": tx.supplier,
            "status": status,
            "diff": diff
        })
        
    return {
        "message": "Processing started",
        "total_received": len(transactions),
        "results": results
    }
