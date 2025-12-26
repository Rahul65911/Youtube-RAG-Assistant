from pydantic import Field
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import ClassVar

BASE_DIR = Path(__file__).resolve().parent.parent

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

    # Database urls
    CHROMA_DIR: ClassVar[Path] = BASE_DIR / "data" / "chroma"
    USER_DB: ClassVar[Path] = f"sqlite:///{(BASE_DIR / 'data' / 'user.db').as_posix()}"
    CHAT_DB: ClassVar[Path] = f"sqlite:///{(BASE_DIR / 'data' / 'chat_history.db').as_posix()}"

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