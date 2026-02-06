# FILE: app/models/schemas.py
from pydantic import BaseModel
from typing import Optional

# Đây là class mà bạn đang viết dở trong ảnh screenshot (api_gateway.py)
# Mình chuyển nó vào đây cho gọn
class Transaction(BaseModel):
    transaction_id: Optional[str] = None
    invoice_amount: float
    po_amount: float
    supplier: str
    bank_account: str
    email: Optional[str] = None
