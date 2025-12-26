from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.db.user_db import engine
from app.models.user_db import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title='RAG Youtube bot', lifespan=lifespan, docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'chrome-extension://eaaamibjpjpkkidgbocdcaegchlcpjfj'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def register_routes(app: FastAPI):
    from app.routes import ingest, rag, auth
    app.include_router(auth.router)
    app.include_router(ingest.router)
    app.include_router(rag.router)

register_routes(app)