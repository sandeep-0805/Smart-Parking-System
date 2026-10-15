from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PaymentOrderResponse(BaseModel):
    razorpay_order_id: str
    amount_paise: int
    currency: str = "INR"
    key_id: str
    booking_id: int

class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    amount_paise: int
    currency: str
    status: str
    refund_amount_paise: Optional[int] = None
    refund_id: Optional[str] = None
    created_at: Optional[datetime] = None
