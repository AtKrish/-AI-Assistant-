ai_chatbot
http://localhost:8000/widget 
uvicorn backend.main:app --reload --port 8001 
uvicorn backend.main:app --reload

py -3.14 -m venv venv314 

source venv314/Scripts/activate

pip install -r requirements.txt


ls venv314/Scripts

🧠 FINAL ARCHITECTURE Frontend (HTML/JS) ↓ FastAPI (/ask) ↓ RAG Pipeline ↓ FAISS (PDF knowledge) ↓ Ollama (LLM)
