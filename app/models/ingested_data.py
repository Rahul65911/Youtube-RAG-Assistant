from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    func,
)
from app.db.user_db import Base 

class YouTubeIngestion(Base):
    __tablename__ = "youtube_ingestions"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, nullable=False, index=True)
    language = Column(String, nullable=False, default="en")
    transcript_hash = Column(String, nullable=False)
    ingested_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "video_id",
            "language",
            name="uq_video_language",
        ),
    )
