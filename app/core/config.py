from pydantic import Field
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application settings
    app_name: str = Field(default="Youtube Chat Bot", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_description: str = Field(default="APIs for Youtube Chat Bot", description="Application description")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment")

    DATA_DIR: Path = Field(default=Path("/data"))

    # Database urls
    CHROMA_DIR: Path = Field(default=Path("/data/chroma"))
    USER_DB: str = Field(
        default="sqlite:////data/user.db",
        description="User database URL"
    )
    CHAT_DB: str = Field(
        default="sqlite:////data/chat_history.db",
        description="Chat history database URL"
    )

    # Text Splitter
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 180

    # Chat History
    MAX_HISTORY_MESSAGES: int = 10

    # JWT
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

@lru_cache()
def get_settings() -> Settings:
    return Settings()