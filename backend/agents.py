"""
3 Agents Xử Lý Logic Audit
"""
import hashlib
import re
from datetime import datetime
from typing import List
import uuid
from models import (
    InvoiceInput, 
    Agent1Output, 
    Agent2Output, 
    Agent3Output,
    TransactionRecord
)

# ============================================
# AGENT 1: INGESTION & SANITIZATION
# ============================================
class Agent1Ingestion:
    """
    Nhiệm vụ:
    - Validate payload
    - Mask PII (email, bank account)
    - Tokenize dữ liệu nhạy cảm
    - Normalize schema
    """
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Che email: abc@xyz.com -> a***@x***.com"""
        if not email or "@" not in email:
            return "N/A"
        local, domain = email.split("@", 1)
        return f"{local[0]}***@{domain[0]}***.{domain.split('.')[-1]}"
    
    @staticmethod
    def mask_bank_account(account: str) -> str:
        """Che STK: 1234567890 -> 123***890"""
        if not account or len(account) < 6:
            return "***"
        return f"{account[:3]}***{account[-3:]}"
    
    @staticmethod
    def validate_amounts(invoice: float, po: float) -> bool:
        """Kiểm tra số tiền hợp lệ"""
        return invoice > 0 and po > 0
    
    def process(self, data: InvoiceInput) -> Agent1Output:
        """Xử lý dữ liệu đầu vào"""
        # Generate transaction ID
        tx_id = str(uuid.uuid4())[:8].upper()
        
        # Validate
        if not self.validate_amounts(data.invoice_amount, data.po_amount):
            status = "rejected"
        else:
            status = "validated"
        
        # Mask PII
        email_masked = self.mask_email(data.email or "")
        bank_masked = self.mask_bank_account(data.bank_account or "")
        
        return Agent1Output(
            transaction_id=tx_id,
            invoice_amount=data.invoice_amount,
            po_amount=data.po_amount,
            supplier=data.supplier,
            email_masked=email_masked,
            bank_account_masked=bank_masked,
            timestamp=datetime.now(),
            status=status
        )

# ============================================
# AGENT 2: MATCHING (PANDAS LOGIC)
# ============================================
class Agent2Matching:
    """
    Nhiệm vụ:
    - So khớp Invoice vs PO
    - Tính toán diff (abs, %)
    - Label: MATCH / MISMATCH
    - Risk level: LOW / MEDIUM / HIGH
    """
    
    THRESHOLD_PERCENTAGE = 5.0  # 5% threshold
    
    @staticmethod
    def calculate_diff(invoice: float, po: float):
        """Tính chênh lệch"""
        diff_amount = abs(invoice - po)
        diff_percentage = (diff_amount / po * 100) if po != 0 else 0
        return diff_amount, diff_percentage
    
    @staticmethod
    def determine_risk(diff_percentage: float) -> str:
        """Xác định mức độ rủi ro"""
        if diff_percentage < 2:
            return "LOW"
        elif diff_percentage < 5:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def process(self, agent1_output: Agent1Output) -> Agent2Output:
        """Phân tích matching"""
        diff_amount, diff_percentage = self.calculate_diff(
            agent1_output.invoice_amount,
            agent1_output.po_amount
        )
        
        # Xác định match status
        match_status = "MATCH" if diff_percentage < self.THRESHOLD_PERCENTAGE else "MISMATCH"
        threshold_exceeded = diff_percentage >= self.THRESHOLD_PERCENTAGE
        risk_level = self.determine_risk(diff_percentage)
        
        return Agent2Output(
            transaction_id=agent1_output.transaction_id,
            diff_amount=diff_amount,
            diff_percentage=round(diff_percentage, 2),
            match_status=match_status,
            threshold_exceeded=threshold_exceeded,
            risk_level=risk_level
        )

# ============================================
# AGENT 3: AI ANALYSIS + HUMAN-IN-THE-LOOP
# ============================================
class Agent3AIAnalysis:
    """
    Nhiệm vụ:
    - Phân tích AI (có thể dùng Gemini/Claude API)
    - Đưa ra verdict
    - Quyết định có cần human review không
    """
    
    def analyze_with_ai(self, agent1_output: Agent1Output, agent2_output: Agent2Output) -> dict:
        """
        STUB: Thay thế bằng Claude/Gemini API call
        """
        # Mock AI analysis
        if agent2_output.risk_level == "HIGH":
            verdict = f"⚠️ HIGH RISK: Invoice-PO mismatch {agent2_output.diff_percentage}% for {agent1_output.supplier}"
            confidence = 0.85
            needs_review = True
            recommendations = [
                "Verify supplier legitimacy",
                "Check historical transactions",
                "Contact procurement team"
            ]
        elif agent2_output.risk_level == "MEDIUM":
            verdict = f"⚡ MEDIUM RISK: {agent2_output.diff_percentage}% deviation detected"
            confidence = 0.70
            needs_review = True
            recommendations = [
                "Review PO terms",
                "Check for partial deliveries"
            ]
        else:
            verdict = f"✅ LOW RISK: Transaction within acceptable range"
            confidence = 0.95
            needs_review = False
            recommendations = ["Auto-approve recommended"]
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "needs_review": needs_review,
            "recommendations": recommendations
        }
    
    def process(self, agent1_output: Agent1Output, agent2_output: Agent2Output) -> Agent3Output:
        """Phân tích AI"""
        ai_result = self.analyze_with_ai(agent1_output, agent2_output)
        
        return Agent3Output(
            transaction_id=agent1_output.transaction_id,
            ai_verdict=ai_result["verdict"],
            confidence_score=ai_result["confidence"],
            recommendations=ai_result["recommendations"],
            requires_human_review=ai_result["needs_review"]
        )

# ============================================
# ORCHESTRATOR: CHẠY CẢ 3 AGENTS
# ============================================
class AuditOrchestrator:
    """
    Điều phối 3 agents theo workflow:
    Input → Agent1 → Agent2 → Agent3 → Output
    """
    
    def __init__(self):
        self.agent1 = Agent1Ingestion()
        self.agent2 = Agent2Matching()
        self.agent3 = Agent3AIAnalysis()
    
    def process_single(self, data: InvoiceInput) -> TransactionRecord:
        """Xử lý 1 invoice qua cả 3 agents"""
        
        # AGENT 1: Ingestion
        a1_output = self.agent1.process(data)
        
        if a1_output.status == "rejected":
            # Skip nếu validation failed
            return TransactionRecord(
                transaction_id=a1_output.transaction_id,
                supplier=a1_output.supplier,
                invoice_amount=a1_output.invoice_amount,
                po_amount=a1_output.po_amount,
                diff_amount=0,
                diff_percentage=0,
                match_status="REJECTED",
                risk_level="N/A",
                requires_human_review=False,
                created_at=a1_output.timestamp,
                updated_at=datetime.now(),
                status="rejected"
            )
        
        # AGENT 2: Matching
        a2_output = self.agent2.process(a1_output)
        
        # AGENT 3: AI Analysis
        a3_output = self.agent3.process(a1_output, a2_output)
        
        # Determine final status
        if a3_output.requires_human_review:
            final_status = "manual_review"
        elif a2_output.match_status == "MATCH":
            final_status = "approved"
        else:
            final_status = "pending"
        
        # Combine vào TransactionRecord
        return TransactionRecord(
            transaction_id=a1_output.transaction_id,
            supplier=a1_output.supplier,
            invoice_amount=a1_output.invoice_amount,
            po_amount=a1_output.po_amount,
            diff_amount=a2_output.diff_amount,
            diff_percentage=a2_output.diff_percentage,
            match_status=a2_output.match_status,
            risk_level=a2_output.risk_level,
            ai_verdict=a3_output.ai_verdict,
            confidence_score=a3_output.confidence_score,
            requires_human_review=a3_output.requires_human_review,
            created_at=a1_output.timestamp,
            updated_at=datetime.now(),
            status=final_status
        )
    
    def process_batch(self, items: List[InvoiceInput]) -> List[TransactionRecord]:
        """Xử lý batch"""
        results = []
        for item in items:
            try:
                result = self.process_single(item)
                results.append(result)
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
        return results
