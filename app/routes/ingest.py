from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound
from fastapi.concurrency import run_in_threadpool

from app.services.ingest import ingest_youtube_threaded
from app.core.schema import YoutubeIngestRequest
from app.auth.dependencies import get_current_user
from app.db.session import get_db

router = APIRouter(prefix='/ingest', tags=['Ingest'])

@router.post("/youtube")
async def ingest_youtube_route(req: YoutubeIngestRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        total_chunks = await run_in_threadpool(ingest_youtube_threaded, req.video_id)
        return {'status': 'success', 'chunks_added': total_chunks}
    
    except TranscriptsDisabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcripts are disabled for this video",
        )

    except NoTranscriptFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No supported transcript found (English or Hindi)",
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest video {e}",
        )
