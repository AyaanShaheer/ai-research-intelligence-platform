from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
from enum import Enum


class ArxivPaper(BaseModel):
    """ArXiv paper model with essential metadata"""
    id: str = Field(description="ArXiv paper ID")
    title: str = Field(description="Paper title")
    authors: List[str] = Field(description="List of authors")
    abstract: str = Field(description="Paper abstract")
    published: datetime = Field(description="Publication date")
    pdf_url: str = Field(description="PDF download URL")
    categories: List[str] = Field(description="ArXiv categories")

class DocumentChunk(BaseModel):
    """Document chunk for vector storage"""
    chunk_id: str = Field(description="Unique chunk identifier")
    paper_id: str = Field(description="Source paper ID")
    content: str = Field(description="Chunk text content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_index: int = Field(description="Chunk position in document")
    
    @classmethod
    def create_chunk_id(cls, paper_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        return hashlib.md5(f"{paper_id}_{chunk_index}".encode()).hexdigest()

class VectorSearchResult(BaseModel):
    """Vector search result with relevance score"""
    paper: ArxivPaper = Field(description="Retrieved paper")
    chunk: DocumentChunk = Field(description="Matching document chunk")
    similarity_score: float = Field(description="Similarity score (0-1)")
    relevance_reason: str = Field(description="Why this result is relevant")

class ResearchQuery(BaseModel):
    """Enhanced research query with vector search options"""
    query: str = Field(description="Research query", min_length=1, max_length=500)
    max_results: Optional[int] = Field(default=5, ge=1, le=20)
    categories: Optional[List[str]] = Field(default=None)
    use_vector_search: bool = Field(default=True, description="Enable semantic search")
    similarity_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

# ... existing imports and models ...

from enum import Enum

class ValidationResult(BaseModel):
    """Validation result from critic agent"""
    overall_score: int = Field(ge=0, le=10, description="Overall quality score")
    accuracy_score: int = Field(ge=0, le=10, description="Accuracy score")
    completeness_score: int = Field(ge=0, le=10, description="Completeness score") 
    relevance_score: int = Field(ge=0, le=10, description="Relevance score")
    hallucination_risk: str = Field(description="Risk level: low/medium/high")
    supported_claims: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: int = Field(ge=0, le=100, description="Confidence percentage")
    papers_count: Optional[int] = Field(default=None)
    summary_length: Optional[int] = Field(default=None)

class AgentState(BaseModel):
    """Enhanced LangGraph agent state with validation"""
    query: str = Field(description="Original user query")
    retrieved_papers: List[ArxivPaper] = Field(default_factory=list)
    vector_results: List[VectorSearchResult] = Field(default_factory=list)
    summaries: List[Dict[str, Any]] = Field(default_factory=list)
    validation: Optional[Dict[str, Any]] = Field(default=None)
    final_response: Optional[str] = Field(default=None)
    step: str = Field(default="retrieval", description="Current processing step")
    iteration_count: int = Field(default=0)
