from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatSessionStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"
    PAUSED = "paused"

class MessageSource(BaseModel):
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    relevance_score: float
    content_preview: str = Field(..., max_length=200)

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    sources: List[MessageSource] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    document_ids: List[str] = Field(default_factory=list)
    status: ChatSessionStatus = ChatSessionStatus.ACTIVE
    message_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

class ChatQuery(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    include_sources: bool = True
    max_sources: int = Field(3, ge=1, le=10)

class ChatResponse(BaseModel):
    message: ChatMessage
    session_id: str
    processing_time: float
    token_usage: Optional[Dict[str, int]] = None

class ChatSessionResponse(BaseModel):
    session: ChatSession
    messages: List[ChatMessage]
    documents: List[Dict[str, Any]] = Field(default_factory=list)

class StartChatRequest(BaseModel):
    document_ids: List[str] = Field(..., min_items=1)
    session_name: Optional[str] = None
    initial_message: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    total_messages: int
    page: int
    page_size: int
