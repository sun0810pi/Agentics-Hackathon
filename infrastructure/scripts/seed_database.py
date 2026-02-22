#!/usr/bin/env python3
# =====================================================
# infrastructure/scripts/seed_database.py
# Seeds the database with sample data for demo
# Run ONCE after initial deployment:
#   python infrastructure/scripts/seed_database.py
# =====================================================

import sys
import os
import uuid
import random
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from services.database import get_db, InvoiceRecord, AuditLog, create_all_tables
from shared.constants import AGENT_NAMES

VENDORS = [
    ("Acme Corporation", "V-001"),
    ("TechSupplies Ltd", "V-002"),
    ("CloudVendor Inc", "V-003"),
    ("Office Depot Pro", "V-004"),
    ("Suspicious Consulting", "V-005"),  # This one will have high risk scores!
]

DECISIONS = ["APPROVE", "APPROVE", "APPROVE", "REVIEW", "BLOCK"]  # Weighted toward APPROVE


def seed_invoices(count: int = 100):
    """Create sample invoice records."""
    print(f"Seeding {count} invoice records...")

    with get_db() as db:
        for i in range(count):
            vendor_name, vendor_id = random.choice(VENDORS)
            decision = random.choice(DECISIONS)

            # Risk score matches decision
            if decision == "APPROVE":
                risk_score = random.uniform(5, 28)
            elif decision == "REVIEW":
                risk_score = random.uniform(31, 68)
            else:
                risk_score = random.uniform(72, 96)

            amount = round(random.uniform(500, 150_000), 2)

            record = InvoiceRecord(
                invoice_id=str(uuid.uuid4()),
                user_id="demo-user-001",
                invoice_number=f"INV-2026-{1000 + i:04d}",
                vendor_name=vendor_name,
                vendor_id=vendor_id,
                amount_total=amount,
                currency="USD",
                decision=decision,
                risk_score=round(risk_score, 1),
                confidence=round(random.uniform(0.75, 0.99), 3),
                processing_time_ms=round(random.uniform(3000, 15000), 0),
                fraud_flags=["HIGH_RISK"] if decision == "BLOCK" else [],
                agent_results=[],
                invoice_data_raw={
                    "invoice_number": f"INV-2026-{1000 + i:04d}",
                    "vendor_name": vendor_name,
                    "amount_total": amount,
                    "currency": "USD",
                },
                audit_hash=uuid.uuid4().hex,
                trace_id=f"1-{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:24]}",
                processed_at=datetime.utcnow() - timedelta(hours=random.randint(0, 720)),
            )
            db.add(record)

    print(f"✅ {count} invoice records seeded!")


def seed_audit_logs(count: int = 200):
    """Create sample audit log entries."""
    print(f"Seeding {count} audit log entries...")

    actions = [
        "INVOICE_ANALYZED", "LOGIN_SUCCESS", "LOGOUT",
        "RATE_LIMIT_HIT", "JWT_VALIDATION_FAILED", "INVOICE_BLOCKED"
    ]

    with get_db() as db:
        for i in range(count):
            action = random.choice(actions)
            log = AuditLog(
                log_id=str(uuid.uuid4()),
                user_id="demo-user-001",
                action=action,
                ip_address=f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                user_agent="AgentFlow-Frontend/3.1.0",
                result="SUCCESS" if "FAILED" not in action and "HIT" not in action else "BLOCKED",
                details={"index": i},
            )
            db.add(log)

    print(f"✅ {count} audit log entries seeded!")


if __name__ == "__main__":
    print("🚀 AgentFlow Database Seeder")
    print("=" * 40)

    # Create tables
    print("Creating database tables...")
    create_all_tables()
    print("✅ Tables created!")

    # Seed data
    seed_invoices(100)
    seed_audit_logs(200)

    print("=" * 40)
    print("✅ Database seeding complete!")
    print("You can now start the backend server.")
