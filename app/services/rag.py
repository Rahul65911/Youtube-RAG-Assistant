from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_cohere import CohereRerank
from langchain_classic.retrievers import ContextualCompressionRetriever
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.db.vectorstore import get_vectorstore

import json

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task='text-generation',
    temperature=0.3,
    streaming=True
)

model = ChatHuggingFace(llm = llm)

prompt = ChatPromptTemplate.from_messages([
    ('system',
        "You are a precise and structured assistant.\n"
        "Answer the question using ONLY the provided context.\n"
        "If the answer is not present in the context, clearly say: 'I do not know.'\n\n"
        "Guidelines for the answer:\n"
        "- Use clear bullet points only (no paragraphs).\n"
        "- Group related points under short, meaningful headings when appropriate.\n"
        "- Keep bullets concise and factual.\n"
        "- Do not add assumptions, examples, or external knowledge.\n\n"
        "Context:\n{context}"
    ),
    # MessagesPlaceholder(variable_name='history'),
    ('human', "{question}")
])

def stream_chain(chain, question):
    try:
        for chunk in chain.stream(question):
            if chunk:
                payload = {
                    "event": "message",
                    "data": chunk
                }

                print(f"{payload}\n\n")
                yield f"{json.dumps(payload)}\n\n"

        yield f"{json.dumps({'event': 'end'})}\n\n"

    except Exception as e:
        yield f"{json.dumps({'event': 'error', 'data': str(e)})}\n\n"

def chat(username: str, video_id: str, question: str):
    # history = get_chat_history(username, video_id)
    # settings = get_settings()

    vector_store = get_vectorstore(video_id)

    base_retriever = vector_store.as_retriever(
        search_type='mmr',
        search_kwargs={
            'k': 10,
            'lambda_mult': 0.4,
            'fetch_k': 20
        }
    )

    reranker = CohereRerank(
        model="rerank-english-v3.0",
        top_n=4
    )

    retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever
    )

    chain = {
        "context": lambda _: retriever.invoke(question),
        "question": RunnablePassthrough(),
        # "history": lambda _: history.messages[-settings.MAX_HISTORY_MESSAGES:]
    } | prompt | model | StrOutputParser()

    # history.add_user_message(question)
    # history.add_ai_message(answer)

    return StreamingResponse(
        stream_chain(chain, question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
