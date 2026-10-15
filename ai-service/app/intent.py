import json
import logging
import re
from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.schemas.intent import IntentResponse

logger = logging.getLogger(__name__)

INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["search", "select_option", "confirm", "cancel_booking", "other"]
        },
        "location_text": {"type": ["string", "null"]},
        "date_text": {"type": ["string", "null"]},
        "start_time_text": {"type": ["string", "null"]},
        "end_time_text": {"type": ["string", "null"]},
        "duration_minutes": {"type": ["integer", "null"]},
        "vehicle_type": {
            "type": ["string", "null"],
            "enum": ["CAR", "MOTORCYCLE", "SUV", "TRUCK", "EV", None]
        },
        "max_budget_inr": {"type": ["number", "null"]},
        "facilities": {
            "type": "array",
            "items": {"type": "string"}
        },
        "option_index": {"type": ["integer", "null"]}
    },
    "required": ["intent"]
}

SYSTEM_PROMPT = """You are an AI parking assistant intent parser.
Your task is to analyze user queries (in English, Hindi, Hinglish, or Telugu) and extract parking booking intents into structured JSON according to the schema.

Rules:
1. Intent must be ONE of: 'search', 'select_option', 'confirm', 'cancel_booking', 'other'.
2. If the user mentions looking for parking, a location, place, or time, intent is 'search'.
3. If the user says 'book the first one', 'first option', 'select 2', etc., intent is 'select_option' and option_index is 1-indexed.
4. If the user confirms or says 'yes proceed', 'confirm booking', 'pay now', intent is 'confirm'.
5. If the user wants to cancel or refund, intent is 'cancel_booking'.
6. Extract raw date phrases ('tomorrow', 'kal', 'next Monday', '15 Oct') as date_text without converting.
7. Extract raw time phrases ('10 AM', 'subah 10 baje', '2:30pm') as start_time_text.
8. Extract duration in minutes if specified ('2 hours' -> 120, '30 mins' -> 30).
9. Vehicle types: CAR, MOTORCYCLE, SUV, TRUCK, EV.
10. Facilities: ev_charging, covered, cctv, disabled_access, valet.
11. Return ONLY the JSON object. Do not hallucinate slot IDs or pricing numbers.
"""

def rule_based_fallback(message: str) -> IntentResponse:
    """Heuristic fallback parser when Ollama is unavailable or times out."""
    lower = message.lower().strip()
    
    # Check select option
    m_opt = re.search(r'\b(?:option|slot|number|no\.?)\s*(\d+)\b', lower)
    if "first" in lower or "1st" in lower:
        return IntentResponse(intent="select_option", option_index=1, confidence=0.8)
    if "second" in lower or "2nd" in lower:
        return IntentResponse(intent="select_option", option_index=2, confidence=0.8)
    if m_opt:
        return IntentResponse(intent="select_option", option_index=int(m_opt.group(1)), confidence=0.8)
    
    # Check confirmation
    if any(k in lower for k in ["confirm", "proceed", "pay now", "ha book karo", "yes book"]):
        return IntentResponse(intent="confirm", confidence=0.9)
        
    # Check cancellation
    if any(k in lower for k in ["cancel", "refund", "radd karo", "stop booking"]):
        return IntentResponse(intent="cancel_booking", confidence=0.9)
        
    # Check search / find
    facilities = []
    if "ev" in lower or "electric" in lower:
        facilities.append("ev_charging")
    if "covered" in lower or "roof" in lower:
        facilities.append("covered")
    if "cctv" in lower or "camera" in lower or "security" in lower:
        facilities.append("cctv")
        
    vehicle_type = "CAR"
    if any(k in lower for k in ["bike", "motorcycle", "scooter", "two wheeler"]):
        vehicle_type = "MOTORCYCLE"
    elif "suv" in lower:
        vehicle_type = "SUV"
    elif "ev" in lower or "electric" in lower:
        vehicle_type = "EV"

    duration = None
    m_dur_h = re.search(r'(\d+)\s*(?:hour|hr|ghante)', lower)
    m_dur_m = re.search(r'(\d+)\s*(?:minute|min|m)', lower)
    if m_dur_h:
        duration = int(m_dur_h.group(1)) * 60
    elif m_dur_m:
        duration = int(m_dur_m.group(1))

    # Basic location extraction heuristic
    location_text = None
    m_loc = re.search(r'(?:near|at|in|around|parking at|parking in|parking near)\s+([a-zA-Z0-9\s]{2,30})', message, re.IGNORECASE)
    if m_loc:
        location_text = m_loc.group(1).split(" for ")[0].split(" at ")[0].strip()

    return IntentResponse(
        intent="search",
        location_text=location_text,
        vehicle_type=vehicle_type,
        facilities=facilities,
        duration_minutes=duration,
        confidence=0.6,
    )

async def extract_intent(
    message: str,
    collected_fields: Dict[str, Any],
    ollama_url: str,
    model: str,
    timeout: float = 20.0,
) -> IntentResponse:
    prompt_context = ""
    if collected_fields:
        prompt_context = f"\nAlready collected parameters: {json.dumps(collected_fields)}\n"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{prompt_context}User query: {message}"}
        ],
        "stream": False,
        "format": INTENT_SCHEMA,
        "options": {
            "temperature": 0.0,
            "num_ctx": 2048,
        },
        "keep_alive": "10m",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{ollama_url}/api/chat", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("message", {}).get("content", "{}")
                parsed = json.loads(content)
                return IntentResponse(**parsed)
            else:
                logger.warning(f"Ollama returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.warning(f"Ollama call failed or timed out: {e}. Using deterministic fallback parser.")

    # Fallback heuristic
    return rule_based_fallback(message)
