from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sqlalchemy.orm import Session
from typing import Tuple
import os
import requests
import hashlib
import re

from dotenv import load_dotenv

from app.core.config import get_settings
from app.db.vectorstore import get_vectorstore
from app.auth.ingested_data import get_ingestion_metadata, upsert_ingestion_metadata
from app.db.user_db import SessionLocal

load_dotenv()

settings = get_settings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP
)

def get_transcript_list(video_id: str):
    return YouTubeTranscriptApi().list(video_id=video_id)

def resolve_transcript(video_id: str) -> Tuple[str, str, str]:
    """
    Returns:
    - transcript text (english)
    - final language ("en")
    - source ("manual" | "auto" | "translated-hi")
    """

    transcript_list = get_transcript_list(video_id)

    # 1. Manual English
    try:
        t = transcript_list.find_manually_created_transcript(["en"])
        data = t.fetch()
        return " ".join(x.text for x in data), "en", "manual"
    except NoTranscriptFound:
        pass

    # 2. Auto English
    try:
        t = transcript_list.find_generated_transcript(["en"])
        data = t.fetch()
        return " ".join(x.text for x in data), "en", "auto"
    except NoTranscriptFound:
        pass

    except NoTranscriptFound:
        pass

    raise NoTranscriptFound("No supported transcript found")

def normalize_text(text: str) -> str:
    """
    Normalize transcript text to avoid false hash mismatches
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)   # normalize whitespace
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    return text.strip()

def hash_text(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

def fetch_video_metadata(video_id: str, api_key: str) -> dict:
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails",
        "id": video_id,
        "key": api_key,
    }

    res = requests.get(url, params=params)
    res.raise_for_status()

    items = res.json().get("items", [])
    if not items:
        raise ValueError("Video not found")

    snippet = items[0]["snippet"]
    content = items[0]["contentDetails"]

    return {
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "channel_name": snippet.get("channelTitle"),
        "published_at": snippet.get("publishedAt"),
        "tags": snippet.get("tags", []),
        "duration": content.get("duration"),
    }

def ingest_youtube_threaded(video_id: str) -> int:
    db = SessionLocal()
    try:
        return ingest_youtube(video_id, db)
    except Exception:
        print("DB Connection failed!")
        raise
    finally:
        db.close()

def ingest_youtube(video_id: str, db: Session) -> int:
    try:
        vector_store = get_vectorstore(video_id)
        
        transcript, language, source = resolve_transcript(video_id)
        
        normalized_transcript = normalize_text(transcript)
        transcript_hash = hash_text(normalized_transcript)
        
        metadata_record = get_ingestion_metadata(db=db, video_id=video_id, language='en') 
        
        if metadata_record and metadata_record.transcript_hash == transcript_hash:
            return 0
        
        vector_store.delete(where={"video_id": video_id})

        metadata = fetch_video_metadata(
            video_id=video_id,
            api_key=os.getenv("YOUTUBE_API_KEY")
        )

        normalized_metadata = {
            **metadata,
            "tags": ", ".join(metadata["tags"]) if metadata.get("tags") else None,
            "language": language,
            "source_type": source,
        }

        Docs = [
            Document(
                page_content=transcript,
                metadata={
                    'source': 'youtube',
                    'video_id': video_id,
                    **normalized_metadata
                }
            )
        ]
        
        chunks = text_splitter.split_documents(Docs)

        try:
            vector_store.add_documents(chunks)
        except Exception as e:
            vector_store.delete(where={"video_id": video_id})
            raise e
        
        upsert_ingestion_metadata(db=db, video_id=video_id, language='en', transcript_hash=transcript_hash)

        return len(chunks)

    except (TranscriptsDisabled, NoTranscriptFound):
        raise