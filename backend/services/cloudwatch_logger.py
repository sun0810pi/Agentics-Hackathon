"""backend/services/cloudwatch_logger.py — Structured JSON logging"""
import json, logging, time
from typing import Dict, Any
logger = logging.getLogger("cloudwatch")

class CloudWatchLogger:
    def __init__(self, service="agentflow-backend"):
        self.service = service

    def _emit(self, level: str, event: str, data: Dict[str, Any]):
        print(json.dumps({"timestamp":time.time(),"level":level,"service":self.service,"event":event,**data}))

    def info(self,    event, **kw): self._emit("INFO",    event, kw)
    def warning(self, event, **kw): self._emit("WARNING", event, kw)
    def error(self,   event, **kw): self._emit("ERROR",   event, kw)

    def invoice_processed(self, invoice_id, decision, risk_score, duration_ms):
        self.info("INVOICE_PROCESSED", invoice_id=invoice_id, decision=decision,
                  risk_score=risk_score, duration_ms=duration_ms)

    def security_alert(self, alert_type, invoice_id, details):
        self.warning("SECURITY_ALERT", alert_type=alert_type, invoice_id=invoice_id, **details)

    def rate_limit_exceeded(self, user_id, endpoint):
        self.warning("RATE_LIMIT_EXCEEDED", user_id=user_id, endpoint=endpoint)

cw_logger = CloudWatchLogger()
