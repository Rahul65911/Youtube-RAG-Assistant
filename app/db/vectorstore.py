from langchain_chroma import Chroma
from app.core.config import get_settings
from dotenv import load_dotenv

load_dotenv()

settings = get_settings()
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        from langchain_cohere import CohereEmbeddings
        _embeddings = CohereEmbeddings(model="embed-v4.0")
    return _embeddings

def get_vectorstore(
    video_id: str,
) -> Chroma:
    """
    Returns a video scoped vector store.
    """
    path = settings.CHROMA_DIR / f"video_{video_id}"
    embedding_model = get_embeddings()

    return Chroma(
        persist_directory=str(path),
        embedding_function=embedding_model,
    )
