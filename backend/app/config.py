import warnings
from pydantic_settings import BaseSettings


_INSECURE_DEFAULT = "change-me-in-production"


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://juflow:juflow_dev@localhost:5432/juflow"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = _INSECURE_DEFAULT
    access_token_expire_minutes: int = 1440
    rsshub_url: str = "http://localhost:1200"
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_claim_email: str = "admin@example.com"
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@juflow.app"
    cors_origins: str = "http://localhost:5173,http://localhost:80"

    model_config = {"env_file": ".env"}


settings = Settings()

if settings.secret_key == _INSECURE_DEFAULT:
    warnings.warn(
        "SECRET_KEY is using the insecure default. Set SECRET_KEY in .env before deploying to production.",
        stacklevel=1,
    )
