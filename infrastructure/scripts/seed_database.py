#!/usr/bin/env python3
"""
scripts/seed_database.py
==========================
Seed database với 100 sample invoices.
Run ONCE sau khi setup AWS: python scripts/seed_database.py
"""
import asyncio, sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))


async def seed():
    from services.database import init_db_pool, init_schema, save_invoice_result, write_audit_log
    from agents.orchestrator import AgentOrchestrator

    print("Connecting to database...")
    await init_db_pool()
    await init_schema()
    print("Schema initialised")

    orch = AgentOrchestrator()
    print("Generating 100 sample invoices...")

    for i in range(100):
        invoice_id = f"INV-SEED-{i+1:04d}"
        result     = await orch.run(invoice_id, "seed_invoice.pdf", b"", mode="demo")
        await save_invoice_result(invoice_id, result)
        await write_audit_log({"event_type":"INVOICE_SEEDED","user_id":"system","invoice_id":invoice_id,
                               "details":{"decision":result["final_decision"]}})
        if (i+1) % 10 == 0:
            print(f"  {i+1}/100 seeded")

    print("✅ Database seeded with 100 invoices")


if __name__ == "__main__":
    asyncio.run(seed())
