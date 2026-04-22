from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "API"
    APP_VERSION: str = "0.0.1"
    
    # Database Config
    DB_CONFIG: str
    DB_ECHO: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    # Optional path to write logs to a plain text file. Leave empty to only log to stdout.
    LOG_FILE: str | None = None
    
    # Security / JWT Config
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
