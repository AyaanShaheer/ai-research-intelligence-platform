from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"

class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., description="Original filename")
    file_type: DocumentType = Field(..., description="Document type")
    description: Optional[str] = Field(None, description="Optional description")

class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    pages: Optional[int] = None
    word_count: Optional[int] = None
    creation_date: Optional[datetime] = None
    language: Optional[str] = None

class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., description="Chunk content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    page_number: Optional[int] = None
    chunk_index: int = Field(..., description="Index in document")
    token_count: Optional[int] = None

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: DocumentType
    status: DocumentStatus = DocumentStatus.UPLOADING
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    description: Optional[str] = None
    chunks_count: Optional[int] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DocumentSummary(BaseModel):
    executive_summary: str
    key_points: List[str]
    main_topics: List[str]
    methodology: Optional[str] = None
    findings: Optional[str] = None
    conclusions: Optional[str] = None
    keywords: List[str]

class DocumentAnalysisResult(BaseModel):
    document_id: str
    summary: DocumentSummary
    insights: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    processing_time: float
    generated_at: datetime = Field(default_factory=datetime.now)

class DocumentListResponse(BaseModel):
    documents: List[Document]
    total_count: int
    page: int
    page_size: int

class DocumentResponse(BaseModel):
    success: bool
    document: Optional[Document] = None
    message: str
    processing_status: Optional[str] = None
