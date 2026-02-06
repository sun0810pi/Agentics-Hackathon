"""
FastAPI Backend - Main Entry Point
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import List
import pandas as pd
import io
from datetime import datetime

from models import (
    InvoiceInput, 
    BatchProcessRequest, 
    BatchProcessResponse,
    TransactionRecord,
    DashboardStats
)
from agents import AuditOrchestrator
from database import db

# ============================================
# FASTAPI APP SETUP
# ============================================
app = FastAPI(
    title="Audit Core V4 API",
    description="Invoice Audit System với 3-Agent Architecture",
    version="4.0.0"
)

# CORS - cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production: chỉ định domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Orchestrator instance
orchestrator = AuditOrchestrator()

# ============================================
# HEALTH CHECK
# ============================================
@app.get("/")
async def root():
    """Root endpoint - serve homepage"""
    return FileResponse("../frontend/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "agent1": "active",
            "agent2": "active",
            "agent3": "active"
        }
    }

# ============================================
# API ENDPOINTS
# ============================================

@app.post("/api/v1/process-batch", response_model=BatchProcessResponse)
async def process_batch(request: BatchProcessRequest):
    """
    Xử lý batch invoices
    
    Input: List[InvoiceInput]
    Output: BatchProcessResponse với results
    """
    try:
        # Update agent status
        db.update_agent_status('agent1', 'active')
        db.update_agent_status('agent2', 'active')
        db.update_agent_status('agent3', 'active')
        
        # Process batch qua orchestrator
        results = orchestrator.process_batch(request.items)
        
        # Save to database
        db.save_batch(results)
        
        # Update stats
        for _ in results:
            db.increment_agent_processed('agent1')
            db.increment_agent_processed('agent2')
            db.increment_agent_processed('agent3')
        
        # Reset agent status
        db.update_agent_status('agent1', 'idle')
        db.update_agent_status('agent2', 'idle')
        db.update_agent_status('agent3', 'idle')
        
        success_count = len([r for r in results if r.status != "rejected"])
        failed_count = len(results) - success_count
        
        return BatchProcessResponse(
            total_processed=len(results),
            success_count=success_count,
            failed_count=failed_count,
            results=results
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Upload Excel file và tự động process
    
    Flow:
    1. Parse Excel → DataFrame
    2. Tìm cột thông minh (invoice, po, supplier...)
    3. Chuyển thành List[InvoiceInput]
    4. Gọi process_batch
    """
    try:
        # Read Excel
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Smart column detection
        inv_col = next((c for c in df.columns if 'invoice' in c or 'hóa đơn' in c or 'amount' in c), None)
        po_col = next((c for c in df.columns if 'po' in c or 'đơn hàng' in c), None)
        sup_col = next((c for c in df.columns if 'supplier' in c or 'nhà cung cấp' in c), None)
        email_col = next((c for c in df.columns if 'email' in c), None)
        acc_col = next((c for c in df.columns if 'account' in c or 'stk' in c or 'bank' in c), None)
        
        if not all([inv_col, po_col, sup_col]):
            raise HTTPException(
                status_code=400, 
                detail="Excel phải có cột: Invoice Amount, PO Amount, Supplier"
            )
        
        # Convert to InvoiceInput list
        items = []
        for _, row in df.iterrows():
            item = InvoiceInput(
                invoice_amount=float(row[inv_col]) if pd.notna(row[inv_col]) else 0.0,
                po_amount=float(row[po_col]) if pd.notna(row[po_col]) else 0.0,
                supplier=str(row[sup_col]) if pd.notna(row[sup_col]) else "UNKNOWN",
                email=str(row[email_col]) if email_col and pd.notna(row[email_col]) else None,
                bank_account=str(row[acc_col]) if acc_col and pd.notna(row[acc_col]) else None
            )
            items.append(item)
        
        # Process batch
        request = BatchProcessRequest(items=items)
        return await process_batch(request)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return db.get_dashboard_stats()

@app.get("/api/v1/transactions", response_model=List[TransactionRecord])
async def get_all_transactions():
    """Lấy tất cả transactions"""
    return db.get_all_transactions()

@app.get("/api/v1/transactions/{tx_id}", response_model=TransactionRecord)
async def get_transaction(tx_id: str):
    """Lấy 1 transaction theo ID"""
    tx = db.get_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@app.get("/api/v1/transactions/status/{status}", response_model=List[TransactionRecord])
async def get_transactions_by_status(status: str):
    """Lọc transactions theo status"""
    return db.get_transactions_by_status(status)

@app.get("/api/v1/agents/stats")
async def get_agent_stats():
    """Lấy stats của 3 agents"""
    return db.get_agent_stats()

@app.post("/api/v1/transactions/{tx_id}/approve")
async def approve_transaction(tx_id: str):
    """Human approve transaction"""
    tx = db.get_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    tx.status = "approved"
    tx.updated_at = datetime.now()
    db.save_transaction(tx)
    
    return {"message": "Transaction approved", "tx_id": tx_id}

@app.post("/api/v1/transactions/{tx_id}/reject")
async def reject_transaction(tx_id: str, reason: str = "Manual rejection"):
    """Human reject transaction"""
    tx = db.get_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    tx.status = "rejected"
    tx.ai_verdict = f"{tx.ai_verdict} | REJECTED: {reason}"
    tx.updated_at = datetime.now()
    db.save_transaction(tx)
    
    return {"message": "Transaction rejected", "tx_id": tx_id}

# ============================================
# NOTIFICATION ENDPOINTS (Slack/Telegram/Zalo)
# ============================================

@app.post("/api/v1/notify/slack")
async def send_slack_notification(webhook_url: str, message: str):
    """Send notification to Slack"""
    import requests
    try:
        response = requests.post(webhook_url, json={"text": message})
        return {"status": "sent", "status_code": response.status_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/notify/telegram")
async def send_telegram_notification(token: str, chat_id: str, message: str):
    """Send notification to Telegram"""
    import requests
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, json={"chat_id": chat_id, "text": message})
        return {"status": "sent", "response": response.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
