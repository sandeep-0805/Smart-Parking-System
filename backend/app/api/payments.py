from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, Header
from app.dependencies import get_current_user
from app.schemas.payments import PaymentOrderResponse, PaymentVerifyRequest
from app.services.payment_service import (
    create_payment_order,
    verify_payment_callback,
    process_razorpay_webhook,
)

router = APIRouter(tags=["Payments"])

@router.post("/bookings/{id}/payment-order", response_model=PaymentOrderResponse)
async def init_booking_payment(
    id: int,
    user: Dict[str, Any] = Depends(get_current_user),
):
    return await create_payment_order(booking_id=id, user_id=user["id"])

@router.post("/payments/verify")
async def verify_payment(
    req: PaymentVerifyRequest,
    _user: Dict[str, Any] = Depends(get_current_user),
):
    return await verify_payment_callback(
        order_id=req.razorpay_order_id,
        payment_id=req.razorpay_payment_id,
        signature=req.razorpay_signature,
    )

@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(..., alias="X-Razorpay-Signature"),
):
    # CRITICAL: Read raw bytes for HMAC verification
    raw_body = await request.body()
    return await process_razorpay_webhook(
        raw_body=raw_body,
        webhook_signature=x_razorpay_signature,
    )
