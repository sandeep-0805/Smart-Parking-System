import asyncio
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Request
from starlette.responses import StreamingResponse
from app.dependencies import get_optional_user
from app.schemas.chat import ChatMessageRequest, ChatResponse
from app.services.chat_service import handle_chat_turn
from app.redis_client import check_rate_limit
from app.exceptions import RateLimitError
from app.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat_message_endpoint(
    req: ChatMessageRequest,
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(f"chat:{client_ip}", settings.RATE_LIMIT_CHAT, 60):
        raise RateLimitError("Chat rate limit exceeded. Please wait a moment.")

    return await handle_chat_turn(
        message=req.message,
        session_id=req.session_id,
        current_user=user,
    )

@router.get("/events")
async def chat_sse_events(
    session_id: str,
    request: Request,
):
    """Server-Sent Events for real-time status updates."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            # Heartbeat ping
            yield f"event: ping\ndata: {json.dumps({'status': 'alive'})}\n\n"
            await asyncio.sleep(15)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
