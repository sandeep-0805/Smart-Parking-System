from fastapi import APIRouter
from app.schemas.quotes import QuoteRequest, QuoteResponse
from app.services.pricing_service import calculate_quote_for_slot

router = APIRouter(prefix="/quotes", tags=["Quotes"])

@router.post("", response_model=QuoteResponse)
async def request_price_quote(req: QuoteRequest):
    return await calculate_quote_for_slot(
        slot_id=req.slot_id,
        start_at=req.start_at,
        end_at=req.end_at,
    )
