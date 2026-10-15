from typing import Any, Optional
from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details},
        )
        self.code = code
        self.message = message
        self.details = details

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(status.HTTP_404_NOT_FOUND, "NOT_FOUND", message, details)

class SlotTakenError(AppException):
    def __init__(self, message: str = "Slot is already booked for this time window", details: Optional[Any] = None):
        super().__init__(status.HTTP_409_CONFLICT, "SLOT_TAKEN", message, details)

class QuoteExpiredError(AppException):
    def __init__(self, message: str = "Price quote has expired. Please request a new quote", details: Optional[Any] = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, "QUOTE_EXPIRED", message, details)

class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required", details: Optional[Any] = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED", message, details)

class ForbiddenError(AppException):
    def __init__(self, message: str = "Access forbidden", details: Optional[Any] = None):
        super().__init__(status.HTTP_403_FORBIDDEN, "FORBIDDEN", message, details)

class AIUnavailableError(AppException):
    def __init__(self, message: str = "AI service is currently unavailable", details: Optional[Any] = None):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, "AI_UNAVAILABLE", message, details)

class RateLimitError(AppException):
    def __init__(self, message: str = "Rate limit exceeded. Try again later", details: Optional[Any] = None):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, "RATE_LIMIT_EXCEEDED", message, details)

class PaymentVerificationError(AppException):
    def __init__(self, message: str = "Payment verification failed", details: Optional[Any] = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, "PAYMENT_FAILED", message, details)
