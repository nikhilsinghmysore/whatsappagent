from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # FastAPI
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    # Database
    database_url: str
    database_echo: bool = False

    # Redis
    redis_url: str

    # WhatsApp
    whatsapp_api_version: str = "v21.0"
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: str
    whatsapp_api_token: str
    whatsapp_verify_token: str
    whatsapp_app_secret: str

    # Claude API
    anthropic_api_key: str
    claude_model: str = "claude-opus-5-5"

    # Encryption
    fernet_key: str

    # Admin
    admin_jwt_secret: str
    admin_jwt_algorithm: str = "HS256"

    # Optional
    google_maps_api_key: Optional[str] = None
    emergency_escalation_email: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
