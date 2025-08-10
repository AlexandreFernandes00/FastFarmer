import os

class Settings:
    PROJECT_NAME: str = "FastFarmer v0.1"
    API_V1_PREFIX: str = "/api/v1"

    _url = os.getenv("DATABASE_URL", "postgresql://...")  # your default
    if _url.startswith("postgres://"):
        _url = _url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL: str = _url

    # 🔐 Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

settings = Settings()
