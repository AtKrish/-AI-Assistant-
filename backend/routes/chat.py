import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import INDEX_PATH, PDF_FOLDER
from services.rag_pipeline import ask_question

router = APIRouter()

class Query(BaseModel):
    query: str

# dummy in-memory
chat_history = []
vector_db = None


def get_vector_db():
    global vector_db

    if vector_db is None:
        index_file = os.path.join(INDEX_PATH, "index.faiss")
        from langchain_community.vectorstores import FAISS
        from models.embeddings import embeddings

        if os.path.exists(index_file):
            vector_db = FAISS.load_local(
                INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            from utils.pdf_loader import load_pdfs

            docs = load_pdfs(PDF_FOLDER)
            if not docs:
                raise HTTPException(
                    status_code=503,
                    detail=f"No PDF content found in {PDF_FOLDER}."
                )

            os.makedirs(INDEX_PATH, exist_ok=True)
            vector_db = FAISS.from_documents(docs, embeddings)
            vector_db.save_local(INDEX_PATH)

    return vector_db


@router.post("/ask")
def ask(q: Query):
    answer = ask_question(get_vector_db(), q.query, chat_history)

    chat_history.append({"user": q.query, "ai": answer})

    return {"answer": answer}
