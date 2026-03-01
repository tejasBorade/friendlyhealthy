from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Healthcare Management Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://localhost:5174"]

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Email (Gmail SMTP)
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_FROM: str = ""  # Your Gmail address
    EMAIL_PASSWORD: str = ""  # Gmail App Password (not your regular password)
    EMAIL_FROM_NAME: str = "Healthcare Platform"
    EMAIL_ENABLED: bool = True
    
    # Legacy (kept for compatibility)
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@healthcareplatform.com"
    FROM_NAME: str = "Healthcare Platform"

    # SMS
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # OTP Settings
    OTP_LENGTH: int = 6
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_LOCKOUT_MINUTES: int = 30

    # Google Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"

    # Firebase (Push Notifications)
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-credentials.json"

    # WhatsApp Business API
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""

    # ABDM (Ayushman Bharat Digital Mission)
    ABDM_CLIENT_ID: str = ""
    ABDM_CLIENT_SECRET: str = ""
    ABDM_BASE_URL: str = "https://dev.abdm.gov.in/gateway"

    # Session Timeouts
    DOCTOR_SESSION_TIMEOUT_MINUTES: int = 10
    PATIENT_SESSION_TIMEOUT_MINUTES: int = 30

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png"]
    UPLOAD_DIR: str = "./uploads"

    # AWS S3
    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    ENCRYPTION_KEY: str = ""  # AES-256 key for at-rest encryption
    SIGNATURE_PIN_SALT: str = ""  # Salt for signature PIN hashing

    # Appointment
    APPOINTMENT_SLOT_DURATION_MINUTES: int = 30
    APPOINTMENT_CANCELLATION_HOURS: int = 24

    # Billing
    TAX_RATE: float = 0.18
    CURRENCY: str = "INR"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
