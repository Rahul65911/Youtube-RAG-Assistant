from sqlalchemy.orm import Session
from app.models.ingested_data import YouTubeIngestion

def get_ingestion_metadata(db: Session, video_id: str, language: str):
    return (
        db.query(YouTubeIngestion)
        .filter_by(
            video_id=video_id,
            language=language,
        )
        .first()
    )

def upsert_ingestion_metadata(
    db: Session,
    video_id: str,
    language: str,
    transcript_hash: str,
):
    record = get_ingestion_metadata(
        db=db,
        video_id=video_id,
        language=language,
    )

    if record:
        record.transcript_hash = transcript_hash
    else:
        record = YouTubeIngestion(
            video_id=video_id,
            language=language,
            transcript_hash=transcript_hash,
        )
        db.add(record)

    db.flush()
    return record
