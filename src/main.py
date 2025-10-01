import os
import logging
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager
import traceback

from fastapi import (
    FastAPI, HTTPException, BackgroundTasks, Depends,
    UploadFile, File, Form
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# ─────────────────── internal imports ────────────────────
from .agents.enhanced_multi_agent import EnhancedMultiAgentPipeline
from .config.settings import settings
from .models.document_models import DocumentResponse, DocumentType
from .models.chat_models import ChatQuery, StartChatRequest
from .services.document_processor import DocumentProcessor
from .services.vector_store_service import VectorStoreService
from .services.chat_service import ChatService

# ─────────────────── logging config ──────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("CiteOnAI")

# ─────────────────── global state ────────────────────────
pipeline: Optional[EnhancedMultiAgentPipeline] = None
document_processor: Optional[DocumentProcessor] = None
vector_store: Optional[VectorStoreService] = None
chat_service: Optional[ChatService] = None

app_metrics = {
    "startup_time": datetime.now(),
    "total_requests": 0,
    "health_checks": 0,
    "research_queries": 0
}

# ─────────────────── FastAPI lifespan ────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, document_processor, vector_store, chat_service

    logger.info("🚀 Starting CiteOn AI Platform...")
    try:
        pipeline = EnhancedMultiAgentPipeline(openai_api_key=settings.openai_api_key)
        document_processor = DocumentProcessor()
        vector_store = VectorStoreService()
        chat_service = ChatService(vector_store)

        health = await pipeline.get_system_health()
        logger.info(f"Platform health: {health['system_status']}")

        logger.info("✅ Services ready: pipeline • docs • vectors • chat")
        yield
    finally:
        logger.info("🛑 Shutting down CiteOn AI Platform")
        logger.info(f"Total requests: {app_metrics['total_requests']}")
        logger.info(f"Research queries: {app_metrics['research_queries']}")

# ─────────────────── FastAPI app ─────────────────────────
app = FastAPI(
    title="CiteOn AI Research Intelligence Platform",
    version="2.0.0",
    description="Enterprise-grade multi-agent research & RAG document system",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────── helper models ───────────────────────
class ResearchQuery(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    max_results: int = Field(10, ge=1, le=50)
    category: Optional[str] = None
    analysis_depth: str = Field("comprehensive")

# ─────────────────── dependency getters ──────────────────
def require_pipeline() -> EnhancedMultiAgentPipeline:
    if not pipeline:
        raise HTTPException(503, "Pipeline not initialised")
    return pipeline

def require_doc_processor() -> DocumentProcessor:
    if not document_processor:
        raise HTTPException(503, "Document processor not initialised")
    return document_processor

def require_vector_store() -> VectorStoreService:
    if not vector_store:
        raise HTTPException(503, "Vector store not initialised")
    return vector_store

def require_chat_service() -> ChatService:
    if not chat_service:
        raise HTTPException(503, "Chat service not initialised")
    return chat_service

# ─────────────────── middleware ──────────────────────────
@app.middleware("http")
async def add_metrics(request, call_next):
    app_metrics["total_requests"] += 1
    start = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start).total_seconds()
    response.headers["X-Process-Time"] = f"{duration:.3f}s"
    return response

# ─────────────────── basic routes ────────────────────────
@app.get("/")
async def root():
    uptime = (datetime.now() - app_metrics["startup_time"]).total_seconds()
    return {
        "service": "CiteOn AI Platform",
        "status": "running",
        "uptime_seconds": uptime,
        "version": "2.0.0",
    }

@app.get("/health")
async def health():
    app_metrics["health_checks"] += 1
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/system-status")
async def system_status():
    """Get system status"""
    try:
        stats = {
            "status": "operational",
            "services": {
                "pipeline": "ready" if pipeline else "not_initialized",
                "document_processor": "ready" if document_processor else "not_initialized", 
                "vector_store": "ready" if vector_store else "not_initialized",
                "chat_service": "ready" if chat_service else "not_initialized"
            },
            "uptime_seconds": (datetime.now() - app_metrics["startup_time"]).total_seconds(),
            "requests_processed": app_metrics["total_requests"]
        }
        
        if vector_store:
            stats["vector_store_stats"] = vector_store.get_stats()
        if chat_service:
            stats["chat_stats"] = chat_service.get_stats()
            
        return stats
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return {"status": "error", "message": str(e)}

# ─────────────────── research route ──────────────────────
@app.post("/research")
async def research(
    payload: ResearchQuery,
    bg: BackgroundTasks,
    pipe: EnhancedMultiAgentPipeline = Depends(require_pipeline)
):
    app_metrics["research_queries"] += 1
    result = await pipe.process_research_query(
        query=payload.query,
        max_papers=payload.max_results,
        category=payload.category,
        analysis_depth=payload.analysis_depth,
    )
    bg.add_task(
        logger.info,
        f"[RESEARCH] {payload.query} → {result.get('papers_analyzed',0)} papers",
    )
    return result

# ─────────────────── FIXED document upload ─────────────────────
@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    bg: BackgroundTasks,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    proc: DocumentProcessor = Depends(require_doc_processor),
    store: VectorStoreService = Depends(require_vector_store),
):
    try:
        # Type / size checks
        ftype = proc.validate_file_type(file.filename)
        if not ftype:
            raise HTTPException(400, "Unsupported file type")
        
        data = await file.read()
        if len(data) > 10 * 1024 * 1024:
            raise HTTPException(400, "File exceeds 10 MB limit")

        logger.info(f"📤 Processing document upload: {file.filename}")
        
        # Process document
        doc = await proc.process_uploaded_file(data, file.filename, ftype, description)
        
        # IMMEDIATE chunk storage - this fixes the issue!
        if doc.status.value == "completed":
            try:
                logger.info(f"🔄 Immediately storing chunks for document {doc.id}")
                
                # Get chunks from document processor
                chunks = await proc.get_document_chunks(doc.id)
                logger.info(f"📝 Retrieved {len(chunks)} chunks from processor")
                
                if chunks:
                    # Store in vector database immediately
                    success = await store.store_document_chunks(doc.id, chunks)
                    if success:
                        logger.info(f"✅ Successfully stored {len(chunks)} chunks in vector store")
                    else:
                        logger.error(f"❌ Failed to store chunks in vector store")
                        
                else:
                    logger.warning(f"⚠️  No chunks retrieved for document {doc.id}")
                    
            except Exception as storage_error:
                logger.error(f"❌ Immediate chunk storage failed: {str(storage_error)}")
                logger.error(f"📍 Storage error traceback: {traceback.format_exc()}")

        logger.info(f"📄 Document upload complete: {doc.filename} (ID: {doc.id})")

        return DocumentResponse(
            success=True,
            document=doc,
            message="Document processed and chunks stored",
            processing_status=doc.status.value,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        logger.error(f"Upload error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ─────────────────── debug endpoints ──────────────────────
@app.post("/debug/fix-document/{document_id}")
async def debug_fix_document(
    document_id: str,
    proc: DocumentProcessor = Depends(require_doc_processor),
    store: VectorStoreService = Depends(require_vector_store)
):
    """Debug endpoint to manually fix chunk storage for a document"""
    try:
        logger.info(f"🔧 Debug: Fixing document {document_id}")
        
        # Get chunks from processor
        chunks = await proc.get_document_chunks(document_id)
        logger.info(f"📝 Debug: Retrieved {len(chunks)} chunks")
        
        if chunks:
            # Show chunk preview
            first_chunk = chunks[0]
            logger.info(f"📖 Debug: First chunk preview: {first_chunk['content'][:200]}...")
            
            # Store in vector database
            success = await store.store_document_chunks(document_id, chunks)
            
            if success:
                logger.info(f"✅ Debug: Successfully stored {len(chunks)} chunks")
                return {
                    "success": True,
                    "document_id": document_id,
                    "chunks_stored": len(chunks),
                    "first_chunk_preview": first_chunk['content'][:200] + "...",
                    "message": "Document fixed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store in vector database"
                }
        else:
            return {
                "success": False,
                "error": "No chunks found in document processor"
            }
            
    except Exception as e:
        logger.error(f"❌ Debug fix error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/debug/documents/{document_id}/chunks")
async def debug_document_chunks(
    document_id: str,
    store: VectorStoreService = Depends(require_vector_store)
):
    """Debug endpoint to check document chunks"""
    chunks = await store.get_document_chunks(document_id)
    stats = store.get_stats()
    
    return {
        "document_id": document_id,
        "chunks_found": len(chunks),
        "chunks": chunks[:3],  # Show first 3 chunks
        "vector_store_stats": stats
    }

@app.get("/debug/chat/sessions")
async def debug_chat_sessions(
    chat: ChatService = Depends(require_chat_service)
):
    """Debug endpoint to check chat sessions"""
    sessions = await chat.get_chat_sessions()
    stats = chat.get_stats()
    
    return {
        "sessions": sessions,
        "chat_stats": stats
    }

# ─────────────────── chat endpoints ──────────────────────
@app.post("/chat/start")
async def chat_start(
    req: StartChatRequest,
    chat: ChatService = Depends(require_chat_service)
):
    session_id = await chat.start_chat_session(req.document_ids, req.session_name)
    return {"session_id": session_id, "documents": len(req.document_ids)}

@app.post("/chat/{session_id}/message")
async def chat_message(
    session_id: str,
    q: ChatQuery,
    chat: ChatService = Depends(require_chat_service)
):
    try:
        result = await chat.send_message(session_id, q.message)
        
        return {
            "ai_response": result['ai_message']['content'],
            "sources": result['ai_message']['sources'],
            "message_id": result['ai_message']['id'],
            "session_id": session_id,
            "sources_count": result['sources_count']
        }
    except Exception as e:
        logger.error(f"Chat message error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{session_id}/history")
async def chat_history(
    session_id: str,
    chat: ChatService = Depends(require_chat_service)
):
    try:
        history = await chat.get_chat_history(session_id)
        return {
            "session_id": session_id,
            "messages": history,
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Chat history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────── error handlers ──────────────────────
@app.exception_handler(HTTPException)
async def http_error(_, exc):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.exception_handler(Exception)
async def unhandled_error(_, exc):
    logger.error(f"Unhandled error: {exc}")
    logger.error(f"Unhandled error traceback: {traceback.format_exc()}")
    return JSONResponse(
        {"detail": "Internal server error"},
        status_code=500,
    )

# ─────────────────── main entrypoint ─────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.debug,
    )
