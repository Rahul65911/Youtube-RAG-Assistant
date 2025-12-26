from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings
from pathlib import Path

settings = get_settings()

Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.USER_DB,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()