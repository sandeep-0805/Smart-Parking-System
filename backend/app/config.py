from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MySQL
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "parking_user"
    MYSQL_PASSWORD: str = "parking_pass"
    MYSQL_DATABASE: str = "smart_parking"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT Authentication
    JWT_SECRET: str = "change-me-to-a-long-random-secret-key-at-least-32-chars"
    JWT_ACCESS_MINUTES: int = 15
    JWT_REFRESH_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # Razorpay (Test Mode)
    RAZORPAY_KEY_ID: str = "rzp_test_placeholder"
    RAZORPAY_KEY_SECRET: str = "placeholder_secret"
    RAZORPAY_WEBHOOK_SECRET: str = "placeholder_webhook_secret"

    # AI Service
    AI_SERVICE_URL: str = "http://ai-service:8001"
    AI_SERVICE_TOKEN: str = "change-me-to-a-service-token"
    AI_SERVICE_TIMEOUT_SECS: float = 2.0

    # Ollama
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_TIMEOUT_SECS: float = 20.0

    # Booking Rules & Defaults
    HOLD_MINUTES: int = 10
    MIN_DURATION_MINUTES: int = 30
    MAX_DURATION_HOURS: int = 24
    BOOKING_GRANULARITY_MINUTES: int = 15
    PER_USER_PENDING_LIMIT: int = 3

    # SMTP Notifications
    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@smartparking.local"
    SMTP_TLS: bool = False

    # App Settings
    APP_NAME: str = "SmartParking"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "Asia/Kolkata"

    # Rate Limiting
    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_REGISTER: int = 3
    RATE_LIMIT_CHAT: int = 20

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
