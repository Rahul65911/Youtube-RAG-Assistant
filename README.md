# 🎥 YouTube RAG Assistant

A **Retrieval-Augmented Generation (RAG)** system that lets users **chat with YouTube videos**.  
It ingests YouTube transcripts and metadata, stores them as embeddings, and answers user questions using contextual retrieval + LLMs.

---

## ✨ Features

- 🔍 Ask questions about any YouTube video  
- 📄 Automatic transcript ingestion  
- 🧠 Semantic search with vector embeddings (ChromaDB)  
- ⚡ Token-level streaming responses (SSE)  
- 🔐 Authentication (JWT-based)  
- 🌐 Web UI / Chrome Extension support  
- 🧩 Modular, production-ready backend  

---

## 🧱 High-Level Architecture

```
Frontend / Chrome Extension
        │
        │  HTTP / SSE
        ▼
FastAPI Backend
 ├── Auth (JWT)
 ├── YouTube Ingestion
 │    └── youtube-transcript-api
 ├── RAG Pipeline (LangChain)
 │    ├── Retriever (Chroma)
 │    ├── Prompt + Context
 │    └── LLM (HuggingFace)
 └── Vector Store (Video-scoped)
```

---

## 🛠 Tech Stack

### Backend
- FastAPI
- LangChain
- ChromaDB
- Cohere / HuggingFace
- YouTube Transcript API
- SQLAlchemy (SQLite)
- Python-JOSE (JWT)
- Passlib (password hashing)

### Frontend
- React + Vite
- Tailwind CSS
- Markdown rendering
- Server-Sent Events (SSE)

---

## 📂 Project Structure

```
app/
├── core/
│   └── config.py
│   └── schema.py
├── auth/
│   └── dependencies.py
│   └── ingested_data.py
│   └── security.py
│   └── users.py
├── routes/
│   ├── auth.py
│   ├── ingest.py
│   └── rag.py
├── services/
│   ├── ingest.py
│   └── rag.py
├── db/
│   ├── user_db.py
│   └── vectorstore.py
│   └── session.py
├── models/
│   └── user_db.py
│   └── ingested_data.py
main.py
```

---

## ⚙️ Environment Variables

Create a `.env` file:

```env
JWT_SECRET_KEY=your_secret
COHERE_API_KEY=your_key
HUGGINGFACE_API_TOKEN=your_token
YOUTUBE_API_KEY=your_key
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/Rahul65911/Youtube-RAG-Assistant.git
cd Youtube-RAG-Assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📄 License

MIT
