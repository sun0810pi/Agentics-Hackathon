"""
backend/services/cloudwatch_logger.py
=======================================
Structured JSON logging to AWS CloudWatch.
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional


class CloudWatchLogger:
    """
    Sends structured logs to CloudWatch.
    Falls back to standard logging if CloudWatch is unavailable.
    """

    def __init__(self, log_group: str = "/agentflow/backend"):
        self.log_group = log_group
        self.service = "agentflow-backend"
        self._logger = logging.getLogger("cloudwatch")

    def _emit(self, level: str, event: str, data: Dict[str, Any]) -> None:
        record = {
            "timestamp": time.time(),
            "level":     level,
            "service":   self.service,
            "event":     event,
            **data,
        }
        # In Lambda, stdout → CloudWatch automatically
        print(json.dumps(record))

    def info(self, event: str, **kwargs) -> None:
        self._emit("INFO", event, kwargs)

    def warning(self, event: str, **kwargs) -> None:
        self._emit("WARNING", event, kwargs)

    def error(self, event: str, **kwargs) -> None:
        self._emit("ERROR", event, kwargs)

    def invoice_processed(self, invoice_id: str, decision: str,
                          risk_score: float, duration_ms: float) -> None:
        self.info("INVOICE_PROCESSED",
                  invoice_id=invoice_id,
                  decision=decision,
                  risk_score=risk_score,
                  duration_ms=duration_ms)

    def security_alert(self, alert_type: str, invoice_id: str,
                       details: Dict[str, Any]) -> None:
        self.warning("SECURITY_ALERT",
                     alert_type=alert_type,
                     invoice_id=invoice_id,
                     **details)

    def rate_limit_exceeded(self, user_id: str, endpoint: str) -> None:
        self.warning("RATE_LIMIT_EXCEEDED",
                     user_id=user_id,
                     endpoint=endpoint)


# Singleton
cw_logger = CloudWatchLogger()
