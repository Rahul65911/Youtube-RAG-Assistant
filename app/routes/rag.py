from fastapi import APIRouter, Depends
from app.core.schema import ChatRequest, ChatResponse
from app.auth.dependencies import get_current_user
from app.services.rag import chat

router = APIRouter(prefix='/chat', tags=['Chat'])

@router.post('')
async def chat_route(req: ChatRequest, user=Depends(get_current_user)):
    return chat(username=user, video_id=req.video_id, question=req.question)