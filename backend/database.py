"""
Database Layer - In-Memory Storage (hoặc DynamoDB)
"""
from typing import List, Optional, Dict
from datetime import datetime
from models import TransactionRecord, DashboardStats

class InMemoryDatabase:
    """
    Simple in-memory database
    Trong production: thay bằng DynamoDB hoặc PostgreSQL
    """
    
    def __init__(self):
        self.transactions: Dict[str, TransactionRecord] = {}
        self.agent_stats = {
            'agent1': {'processed': 0, 'failed': 0, 'status': 'idle'},
            'agent2': {'processed': 0, 'failed': 0, 'status': 'idle'},
            'agent3': {'processed': 0, 'failed': 0, 'status': 'idle'},
        }
    
    def save_transaction(self, record: TransactionRecord):
        """Lưu transaction"""
        self.transactions[record.transaction_id] = record
    
    def save_batch(self, records: List[TransactionRecord]):
        """Lưu nhiều transactions"""
        for record in records:
            self.save_transaction(record)
    
    def get_transaction(self, tx_id: str) -> Optional[TransactionRecord]:
        """Lấy 1 transaction"""
        return self.transactions.get(tx_id)
    
    def get_all_transactions(self) -> List[TransactionRecord]:
        """Lấy tất cả transactions"""
        return list(self.transactions.values())
    
    def get_transactions_by_status(self, status: str) -> List[TransactionRecord]:
        """Lọc theo status"""
        return [tx for tx in self.transactions.values() if tx.status == status]
    
    def get_dashboard_stats(self) -> DashboardStats:
        """Tính toán stats cho dashboard"""
        all_tx = list(self.transactions.values())
        
        return DashboardStats(
            total_transactions=len(all_tx),
            pending_review=len([tx for tx in all_tx if tx.status == "manual_review"]),
            approved=len([tx for tx in all_tx if tx.status == "approved"]),
            rejected=len([tx for tx in all_tx if tx.status == "rejected"]),
            total_amount=sum(tx.invoice_amount for tx in all_tx),
            avg_processing_time=0.0,  # Mock
            high_risk_count=len([tx for tx in all_tx if tx.risk_level == "HIGH"])
        )
    
    def update_agent_status(self, agent_name: str, status: str):
        """Update agent status"""
        if agent_name in self.agent_stats:
            self.agent_stats[agent_name]['status'] = status
    
    def increment_agent_processed(self, agent_name: str):
        """Tăng counter processed"""
        if agent_name in self.agent_stats:
            self.agent_stats[agent_name]['processed'] += 1
    
    def get_agent_stats(self):
        """Lấy stats của agents"""
        return self.agent_stats

# Global database instance
db = InMemoryDatabase()
