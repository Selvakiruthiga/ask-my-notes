import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.document_processor import process_document
from backend.vector_store import add_chunks_to_store, clear_store, get_all_chunks
from backend.retriever import hybrid_retrieve
from backend.generator import generate_answer, generate_quiz

app = FastAPI(title="Ask-My-Notes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_POSSIBLE_SCORE = 2 / 61
MAX_UPLOAD_MB = 10


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # keep only the base name so a crafted filename cannot write outside uploads
    safe_name = os.path.basename(file.filename or "notes.pdf")
    if not safe_name.lower().endswith(".pdf"):
        return JSONResponse({"message": "Only PDF files are allowed."}, status_code=400)

    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if os.path.getsize(file_path) > MAX_UPLOAD_MB * 1024 * 1024:
        os.remove(file_path)
        return JSONResponse({"message": f"File is larger than {MAX_UPLOAD_MB} MB."}, status_code=400)

    chunks = process_document(file_path)
    doc_id = str(uuid.uuid4())
    add_chunks_to_store(chunks, doc_id)

    return {
        "message": "File processed successfully",
        "chunks_created": len(chunks)
    }


@app.post("/ask")
async def ask_question(question: str = Form(...)):
    results = hybrid_retrieve(question)
    top_chunks = [chunk for chunk, score in results]
    top_score = results[0][1] if results else 0

    confidence = min(100, round((top_score / MAX_POSSIBLE_SCORE) * 100)) if results else 0

    try:
        answer = generate_answer(top_chunks, question)
    except Exception:
        # most often the free Gemini limit; show a friendly message instead of a crash
        answer = "The AI service is busy right now. Please wait a minute and try again."

    return {
        "question": question,
        "answer": answer,
        "sources": top_chunks,
        "confidence": confidence
    }


@app.post("/quiz")
async def quiz_endpoint():
    chunks = get_all_chunks()
    if not chunks:
        return {"questions": []}

    combined_text = "\n\n".join(chunks[:10])
    try:
        questions = generate_quiz(combined_text)
    except Exception:
        questions = []

    return {"questions": questions}


@app.post("/reset")
async def reset_store():
    clear_store()
    return {"message": "Store cleared successfully"}


@app.get("/api/status")
async def status():
    return {"status": "Ask-My-Notes backend is running"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
