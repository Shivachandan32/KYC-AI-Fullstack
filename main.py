# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import time

load_dotenv()

from rag_service import RAGService
from llm_service import LLMService
from database import Database

app = FastAPI(
    title="KYC-AI Verification System",
    description="AI-powered document verification with RAG-based explanations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 Starting KYC-AI system...")
rag_service = RAGService()
llm_service = LLMService(rag_service)
db = Database()
print("✅ System ready!")

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def root():
    return {"status": "running", "message": "KYC-AI System is live"}


@app.post("/verify-document")
async def verify_document(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not supported."
        )

    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )

    print(f"📥 Received file: {file.filename} ({file.content_type})")

    try:
        # Track processing time — real metric for resume
        start_time = time.time()
        result = llm_service.verify_document(file_bytes, file.content_type)
        processing_time = time.time() - start_time

        # Save to MongoDB
        record_id = db.save_verification(
            filename=file.filename,
            file_type=file.content_type,
            result=result,
            processing_time=processing_time
        )

        return {
            "success": True,
            "filename": file.filename,
            "processing_time_seconds": round(processing_time, 2),
            "record_id": record_id,
            "result": result
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "rag_initialized": True,
        "llm_model": "llama-4-scout",
        "embedding_model": "sentence-transformers",
        "database": "mongodb"
    }


@app.get("/dashboard-stats")
def dashboard_stats():
    """Returns real verification stats for the Chart.js dashboard."""
    try:
        stats = db.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))