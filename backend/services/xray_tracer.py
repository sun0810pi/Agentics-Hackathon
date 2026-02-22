"""backend/services/xray_tracer.py — AWS X-Ray distributed tracing"""
import time, logging, functools, uuid
from typing import Optional, Callable, Any
from contextlib import contextmanager
logger = logging.getLogger(__name__)

try:
    from aws_xray_sdk.core import xray_recorder, patch_all
    XRAY_AVAILABLE = True
except ImportError:
    XRAY_AVAILABLE = False


def init_xray(service: str = "agentflow-backend"):
    if not XRAY_AVAILABLE: return
    try:
        xray_recorder.configure(service=service, sampling=True, context_missing="LOG_ERROR")
        patch_all()
        logger.info(f"X-Ray ready: {service}")
    except Exception as e:
        logger.warning(f"X-Ray init: {e}")


@contextmanager
def xray_subsegment(name: str, metadata: Optional[dict] = None):
    if not XRAY_AVAILABLE: yield; return
    try:
        with xray_recorder.in_subsegment(name) as seg:
            if metadata:
                for k,v in metadata.items(): seg.put_metadata(k,v)
            start = time.time()
            try: yield seg
            except Exception as e: seg.add_exception(e, fatal=True); raise
            finally: seg.put_annotation("duration_ms", round((time.time()-start)*1000,2))
    except Exception as e:
        logger.warning(f"X-Ray subsegment ({name}): {e}")
        yield


def get_trace_id() -> str:
    if not XRAY_AVAILABLE: return f"1-{hex(int(time.time()))[2:]}-{uuid.uuid4().hex[:24]}"
    try:
        seg = xray_recorder.current_segment()
        return seg.trace_id if seg else f"1-{hex(int(time.time()))[2:]}-{uuid.uuid4().hex[:24]}"
    except: return f"1-{hex(int(time.time()))[2:]}-{uuid.uuid4().hex[:24]}"


def get_demo_trace_data(invoice_id: str) -> dict:
    import random
    trace_id = f"1-{hex(int(time.time()))[2:]}-{uuid.uuid4().hex[:24]}"
    base = time.time() * 1000
    agents = [
        ("agent_0_ocr",45,"Textract"),("agent_1_pii",8,"In-process"),("agent_2_decimal",5,"In-process"),
        ("agent_3_ai_analyst",280,"Bedrock"),("agent_4_audit",6,"In-process"),("agent_5_notifier",35,"SNS"),
        ("agent_6_dashboard",4,"In-process"),("agent_7_integrator",22,"External API"),
        ("agent_8_ml_insights",90,"SageMaker"),("agent_9_learning",12,"DynamoDB"),("agent_10_currency",18,"ExchangeRate API"),
        ("agent_11_merchant",15,"In-process"),("agent_12_quality",7,"In-process"),("agent_13_trend",25,"In-process"),
        ("agent_14_security",40,"In-process"),("agent_15_fraud_ring",65,"Neptune"),("agent_16_behavioral",30,"In-process"),
    ]
    segs, cursor = [], base
    for name, base_ms, svc in agents:
        dur = base_ms + random.randint(-5,20)
        segs.append({"id":uuid.uuid4().hex[:16],"name":name,"start_time":cursor/1000,"end_time":(cursor+dur)/1000,
            "duration_ms":dur,"service":svc,"error":random.random()<0.02,"annotations":{"invoice_id":invoice_id}})
        cursor += dur * 0.7
    return {"trace_id":trace_id,"invoice_id":invoice_id,"duration_ms":round(cursor-base,2),
            "start_time":base/1000,"end_time":cursor/1000,"subsegments":segs,
            "service_map":[{"from":"API Gateway","to":"Lambda"},{"from":"Lambda","to":"Textract"},
                           {"from":"Lambda","to":"Bedrock"},{"from":"Lambda","to":"RDS PostgreSQL"}]}
