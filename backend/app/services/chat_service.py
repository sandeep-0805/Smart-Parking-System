import json
import logging
import uuid
from typing import Dict, Any, Optional, List, Tuple
from app.config import settings
from app.redis_client import get_cache, set_cache
from app.services.ai_client import ai_client
from app.services.booking_service import create_booking_reservation, cancel_booking
from app.services.search_service import search_parking
from app.schemas.chat import ChatResponse, ChatOption

logger = logging.getLogger("chat_service")

async def get_or_create_session(session_id: Optional[str]) -> Tuple[str, Dict[str, Any]]:
    sid = session_id or str(uuid.uuid4())
    cached = await get_cache(f"chat_sess:{sid}")
    if cached and isinstance(cached, dict):
        return sid, cached
    initial = {
        "collected_fields": {},
        "last_options": [],
        "pending_booking_id": None,
    }
    await set_cache(f"chat_sess:{sid}", initial, 1800)  # 30-minute TTL
    return sid, initial

async def save_session(session_id: str, state: Dict[str, Any]):
    await set_cache(f"chat_sess:{session_id}", state, 1800)

async def handle_chat_turn(
    message: str,
    session_id: Optional[str],
    current_user: Optional[Dict[str, Any]],
) -> ChatResponse:
    sid, state = await get_or_create_session(session_id)
    collected = state.get("collected_fields", {})
    last_options = state.get("last_options", [])

    # 1. Call AI service for structured intent
    intent_data = await ai_client.extract_intent(
        message=message,
        collected_fields=collected,
    )

    if not intent_data:
        # Fallback FR-C7: Ollama down or timed out
        return ChatResponse(
            reply="I couldn't quite understand that. You can easily use our search form with your preferences pre-filled:",
            session_id=sid,
            intent="other",
            action_type="redirect_search",
            prefill_search=collected,
        )

    intent = intent_data.get("intent", "other")

    # Update collected fields with any newly extracted parameters
    for k in ["location_text", "date_text", "start_time_text", "duration_minutes", "vehicle_type", "max_budget_inr"]:
        val = intent_data.get(k)
        if val is not None:
            collected[k] = val
    if intent_data.get("facilities"):
        curr_facs = set(collected.get("facilities", []))
        curr_facs.update(intent_data["facilities"])
        collected["facilities"] = list(curr_facs)
    state["collected_fields"] = collected

    # ── Intent 1: select_option ("Book the first one") ────────────────────────
    if intent == "select_option":
        opt_idx = intent_data.get("option_index", 1) or 1
        matched_opt = None
        for opt in last_options:
            if opt.get("option_index") == opt_idx:
                matched_opt = opt
                break
        if not matched_opt and last_options:
            matched_opt = last_options[0]

        if not matched_opt:
            return ChatResponse(
                reply="I couldn't find the option you mentioned. Please tell me where and when you'd like to park first.",
                session_id=sid,
                intent="search",
            )

        if not current_user:
            await save_session(sid, state)
            return ChatResponse(
                reply=f"Option #{matched_opt['option_index']} at {matched_opt['location_name']} (₹{matched_opt['total_price_paise']/100:.2f}) looks great! Please log in to complete your booking reservation.",
                session_id=sid,
                intent="select_option",
                requires_login=True,
            )

        # User is logged in: create the reservation
        try:
            booking = await create_booking_reservation(
                user_id=current_user["user_id"],
                quote_id=matched_opt["quote_id"],
                source="CHAT",
            )
            state["pending_booking_id"] = booking["id"]
            await save_session(sid, state)

            reply_msg = (
                f"🎉 Great choice! I have reserved **Slot {booking['slot_code']}** at **{booking['location_name']}** for you. "
                f"Total amount: **₹{booking['total_paise']/100:.2f}**. "
                f"Your 10-minute hold is active. Click below to proceed with payment."
            )
            return ChatResponse(
                reply=reply_msg,
                session_id=sid,
                intent="confirm",
                action_type="payment_ready",
                booking_id=booking["id"],
            )
        except Exception as e:
            return ChatResponse(
                reply=f"Sorry, that slot couldn't be reserved: {str(e)}. Would you like me to find alternatives?",
                session_id=sid,
                intent="search",
            )

    # ── Intent 2: confirm ─────────────────────────────────────────────────────
    if intent == "confirm":
        if state.get("pending_booking_id"):
            b_id = state["pending_booking_id"]
            return ChatResponse(
                reply=f"Your booking reservation #{b_id} is waiting. Please complete payment to confirm:",
                session_id=sid,
                intent="confirm",
                action_type="payment_ready",
                booking_id=b_id,
            )
        return ChatResponse(
            reply="You don't have a pending reservation to confirm. Where would you like to park?",
            session_id=sid,
            intent="search",
        )

    # ── Intent 3: cancel_booking ──────────────────────────────────────────────
    if intent == "cancel_booking":
        if not current_user:
            return ChatResponse(
                reply="Please log in to your account to view or cancel your active bookings.",
                session_id=sid,
                intent="cancel_booking",
                requires_login=True,
            )
        return ChatResponse(
            reply="You can cancel your booking directly from your 'My Bookings' tab, where refund amounts are calculated automatically according to the policy.",
            session_id=sid,
            intent="cancel_booking",
            action_type="redirect_search",
        )

    # ── Intent 4: search ──────────────────────────────────────────────────────
    if intent == "search" or collected.get("location_text"):
        # Check if required field missing: ask follow-up template question
        if not collected.get("location_text"):
            await save_session(sid, state)
            return ChatResponse(
                reply="Which area or landmark in Hyderabad would you like to park near? (e.g. Hitech City, Gachibowli, Inorbit Mall)",
                session_id=sid,
                intent="search",
            )

        # Execute search deterministically from DB
        prefs = current_user.get("preferences", {}) if current_user else {}
        budget_paise = int(collected["max_budget_inr"] * 100) if collected.get("max_budget_inr") else None

        search_res = await search_parking(
            user_preferences=prefs,
            place_name=collected.get("location_text"),
            date_text=collected.get("date_text"),
            start_time_text=collected.get("start_time_text"),
            duration_minutes=collected.get("duration_minutes", 120),
            vehicle_type=collected.get("vehicle_type", "CAR"),
            max_budget_paise=budget_paise,
            facilities=collected.get("facilities", []),
        )

        chat_options: List[ChatOption] = []
        opt_num = 1
        for loc in search_res.get("locations", [])[:3]:
            for slot in loc.get("slots", [])[:1]:
                chat_options.append(ChatOption(
                    option_index=opt_num,
                    slot_id=slot["slot_id"],
                    quote_id=slot["quote_id"],
                    location_id=loc["location_id"],
                    location_name=loc["name"],
                    address=loc["address"],
                    slot_code=slot["slot_code"],
                    total_price_paise=slot["total_price_paise"],
                    price_formatted=f"₹{slot['total_price_paise']/100:.2f}",
                    distance_m=loc["distance_m"],
                    reason_tags=slot.get("reason_tags", []),
                ))
                opt_num += 1

        state["last_options"] = [o.model_dump() for o in chat_options]
        await save_session(sid, state)

        if not chat_options:
            return ChatResponse(
                reply=f"I couldn't find any available parking slots near '{collected.get('location_text')}' for that time. Would you like to try another area or vehicle type?",
                session_id=sid,
                intent="search",
            )

        reply_text = f"I found {len(chat_options)} great parking options near {collected.get('location_text')}. You can reply 'Book the first one' or select below:"
        return ChatResponse(
            reply=reply_text,
            session_id=sid,
            intent="search",
            options=chat_options,
            action_type="show_options",
        )

    # Generic other intent
    await save_session(sid, state)
    return ChatResponse(
        reply="Hello! I'm your Smart Parking assistant. You can ask me things like 'Find parking near Hitech City tomorrow for 2 hours' or 'Book the closest slot with EV charging'.",
        session_id=sid,
        intent="other",
    )
