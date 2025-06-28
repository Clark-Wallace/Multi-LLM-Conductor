from pydantic_settings import BaseSettings
from typing import Optional
import os
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "ServiceConnect"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security - CRITICAL: Use environment variables in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 4  # 4 hours (reduced from 7 days)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    
    # Security Settings
    BCRYPT_ROUNDS: int = 12
    FAILED_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    PASSWORD_MIN_LENGTH: int = 12
    REQUIRE_2FA: bool = True
    
    # OPSEC Settings
    ENABLE_OPSEC_SCREENING: bool = True
    LOCATION_SCRUBBING: bool = True
    DEPLOYMENT_BLACKOUT_CHECK: bool = True
    
    # Database
    POSTGRES_USER: str = "serviceconnect"
    POSTGRES_PASSWORD: str = "serviceconnect"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "serviceconnect"
    DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # Military Verification (placeholder for actual integration)
    MILITARY_VERIFICATION_API_KEY: Optional[str] = None
    MILITARY_VERIFICATION_API_URL: Optional[str] = None
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = "ServiceConnect"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()