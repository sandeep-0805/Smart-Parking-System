import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "smart_parking"
    MYSQL_AI_USER: str = "ai_reader"
    MYSQL_AI_PASSWORD: str = "ai_reader_pass"

    AI_SERVICE_TOKEN: str = "change-me-to-a-service-token"

    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_TIMEOUT_SECS: float = 20.0

    MODEL_ARTIFACTS_DIR: str = os.getenv("MODEL_ARTIFACTS_DIR", "/app/model_artifacts")
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
