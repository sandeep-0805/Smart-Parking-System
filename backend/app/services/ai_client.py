import logging
import time
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger("ai_client")

class AIClient:
    def __init__(
        self,
        base_url: str = settings.AI_SERVICE_URL,
        token: str = settings.AI_SERVICE_TOKEN,
        timeout: float = settings.AI_SERVICE_TIMEOUT_SECS,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.failure_count = 0
        self.circuit_open_until: float = 0.0

    def _is_circuit_open(self) -> bool:
        if self.circuit_open_until > time.time():
            return True
        return False

    def _record_success(self):
        self.failure_count = 0
        self.circuit_open_until = 0.0

    def _record_failure(self):
        self.failure_count += 1
        if self.failure_count >= 5:
            self.circuit_open_until = time.time() + 30.0  # Open for 30s
            logger.warning("Circuit breaker opened for ai-service (5 consecutive failures).")

    async def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        if self._is_circuit_open():
            logger.info("Circuit breaker OPEN. Skipping AI rank call.")
            return None

        url = f"{self.base_url}/v1/rank"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Service-Token": self.token,
        }
        payload = {
            "candidates": candidates,
            "preferences": preferences,
            "weights": weights or {
                "distance": 0.35,
                "price": 0.30,
                "availability": 0.15,
                "facilities": 0.20,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    self._record_success()
                    data = resp.json()
                    return data.get("ranked", [])
                else:
                    logger.warning(f"AI rank failed: {resp.status_code} {resp.text}")
                    self._record_failure()
                    return None
        except Exception as e:
            logger.warning(f"AI rank call exception: {e}")
            self._record_failure()
            return None

    async def extract_intent(
        self,
        message: str,
        collected_fields: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Dict[str, Any]]:
        if self._is_circuit_open():
            return None

        url = f"{self.base_url}/v1/intent"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Service-Token": self.token,
        }
        payload = {
            "message": message,
            "collected_fields": collected_fields,
            "conversation_history": conversation_history or [],
        }

        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECS) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    self._record_success()
                    return resp.json()
                else:
                    self._record_failure()
                    return None
        except Exception as e:
            logger.warning(f"AI intent call exception: {e}")
            self._record_failure()
            return None

    async def get_forecast(
        self,
        location_id: int,
        target_time: str,
    ) -> Optional[Dict[str, Any]]:
        if self._is_circuit_open():
            return None

        url = f"{self.base_url}/v1/forecast"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Service-Token": self.token,
        }
        payload = {
            "location_id": location_id,
            "target_time": target_time,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    self._record_success()
                    return resp.json()
                else:
                    self._record_failure()
                    return None
        except Exception as e:
            logger.warning(f"AI forecast call exception: {e}")
            self._record_failure()
            return None

ai_client = AIClient()
