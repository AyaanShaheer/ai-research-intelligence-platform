import os
import pickle
import logging
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

from ..models.schemas import ArxivPaper, DocumentChunk, VectorSearchResult

logger = logging.getLogger(__name__)

class VectorStoreService:
    """FAISS-based vector store service for semantic search"""
    
    def __init__(self, 
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 index_path: str = "data/faiss_index",
                 chunk_size: int = 512,
                 chunk_overlap: int = 50):
        """Initialize vector store service"""
        self.model_name = model_name
        self.index_path = Path(index_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize sentence transformer for direct embedding
        self.sentence_model = SentenceTransformer(model_name)
        
        # Initialize or load FAISS index
        self.vector_store = None
        self.paper_metadata = {}  # Store paper metadata separately
        self._ensure_index_directory()
        self._load_or_create_index()
    
    def _ensure_index_directory(self):
        """Ensure index directory exists"""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        try:
            if self.index_path.exists():
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                self.vector_store = FAISS.load_local(
                    str(self.index_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self._load_metadata()
            else:
                logger.info("Creating new FAISS index")
                # Create empty index with sample document
                sample_doc = Document(page_content="initialization", metadata={"type": "init"})
                self.vector_store = FAISS.from_documents([sample_doc], self.embeddings)
                
        except Exception as e:
            logger.error(f"Error loading/creating FAISS index: {e}")
            # Fallback to empty index
            sample_doc = Document(page_content="initialization", metadata={"type": "init"})
            self.vector_store = FAISS.from_documents([sample_doc], self.embeddings)
    
    def _save_metadata(self):
        """Save paper metadata to disk"""
        metadata_path = self.index_path.parent / "paper_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.paper_metadata, f)
    
    def _load_metadata(self):
        """Load paper metadata from disk"""
        metadata_path = self.index_path.parent / "paper_metadata.pkl"
        if metadata_path.exists():
            with open(metadata_path, 'rb') as f:
                self.paper_metadata = pickle.load(f)
        else:
            self.paper_metadata = {}
    
    def chunk_paper_content(self, paper: ArxivPaper) -> List[DocumentChunk]:
        """Split paper content into chunks for vector storage"""
        chunks = []
        
        # Combine title and abstract for chunking
        full_content = f"Title: {paper.title}\n\nAbstract: {paper.abstract}"
        
        # Simple text chunking (can be enhanced with more sophisticated methods)
        content_length = len(full_content)
        start = 0
        chunk_index = 0
        
        while start < content_length:
            end = min(start + self.chunk_size, content_length)
            chunk_content = full_content[start:end]
            
            # Create document chunk
            chunk = DocumentChunk(
                chunk_id=DocumentChunk.create_chunk_id(paper.id, chunk_index),
                paper_id=paper.id,
                content=chunk_content,
                metadata={
                    "title": paper.title,
                    "authors": paper.authors,
                    "categories": paper.categories,
                    "published": paper.published.isoformat(),
                    "pdf_url": paper.pdf_url
                },
                chunk_index=chunk_index
            )
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            chunk_index += 1
            
            # Prevent infinite loop
            if start >= end:
                break
        
        logger.info(f"Created {len(chunks)} chunks for paper {paper.id}")
        return chunks
    
    async def add_papers_to_index(self, papers: List[ArxivPaper]) -> int:
        """Add papers to the vector index"""
        documents_to_add = []
        papers_added = 0
        
        for paper in papers:
            # Skip if paper already indexed
            if paper.id in self.paper_metadata:
                logger.info(f"Paper {paper.id} already in index, skipping")
                continue
            
            # Create chunks for the paper
            chunks = self.chunk_paper_content(paper)
            
            # Convert chunks to LangChain documents
            for chunk in chunks:
                doc = Document(
                    page_content=chunk.content,
                    metadata={
                        "chunk_id": chunk.chunk_id,
                        "paper_id": chunk.paper_id,
                        "chunk_index": chunk.chunk_index,
                        **chunk.metadata
                    }
                )
                documents_to_add.append(doc)
            
            # Store paper metadata
            self.paper_metadata[paper.id] = paper.model_dump()
            papers_added += 1
        
        if documents_to_add:
            # Add documents to FAISS index
            if len(self.vector_store.docstore._dict) == 1:
                # Replace initialization document
                self.vector_store = FAISS.from_documents(documents_to_add, self.embeddings)
            else:
                # Add to existing index
                self.vector_store.add_documents(documents_to_add)
            
            # Save index and metadata
            self._save_index()
            self._save_metadata()
            
            logger.info(f"Added {papers_added} papers ({len(documents_to_add)} chunks) to vector index")
        
        return papers_added
    
    async def semantic_search(self, 
                            query: str, 
                            k: int = 5, 
                            similarity_threshold: float = 0.5) -> List[VectorSearchResult]:
        """Perform semantic search using vector similarity"""
        try:
            if not self.vector_store or len(self.vector_store.docstore._dict) <= 1:
                logger.warning("Vector store is empty or not initialized")
                return []
            
            # Perform similarity search with scores
            docs_and_scores = self.vector_store.similarity_search_with_score(
                query, k=k
            )
            
            results = []
            for doc, score in docs_and_scores:
                # Convert distance to similarity score (FAISS uses L2 distance)
                similarity_score = max(0.0, 1.0 - score / 2.0)  # Normalize distance
                
                if similarity_score < similarity_threshold:
                    continue
                
                # Get paper metadata
                paper_id = doc.metadata.get("paper_id")
                if paper_id and paper_id in self.paper_metadata:
                    paper_data = self.paper_metadata[paper_id]
                    paper = ArxivPaper(**paper_data)
                    
                    # Create document chunk
                    chunk = DocumentChunk(
                        chunk_id=doc.metadata.get("chunk_id", "unknown"),
                        paper_id=paper_id,
                        content=doc.page_content,
                        metadata=doc.metadata,
                        chunk_index=doc.metadata.get("chunk_index", 0)
                    )
                    
                    # Generate relevance reason
                    relevance_reason = self._generate_relevance_reason(query, doc.page_content)
                    
                    result = VectorSearchResult(
                        paper=paper,
                        chunk=chunk,
                        similarity_score=similarity_score,
                        relevance_reason=relevance_reason
                    )
                    results.append(result)
            
            logger.info(f"Found {len(results)} relevant results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    def _generate_relevance_reason(self, query: str, content: str) -> str:
        """Generate explanation for why content is relevant"""
        # Simple keyword matching for relevance explanation
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        common_words = query_words.intersection(content_words)
        
        if common_words:
            return f"Contains relevant terms: {', '.join(list(common_words)[:5])}"
        else:
            return "Semantically related content based on vector similarity"
    
    def _save_index(self):
        """Save FAISS index to disk"""
        try:
            self.vector_store.save_local(str(self.index_path))
            logger.info(f"Saved FAISS index to {self.index_path}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        if not self.vector_store:
            return {"status": "not_initialized"}
        
        return {
            "total_documents": len(self.vector_store.docstore._dict),
            "total_papers": len(self.paper_metadata),
            "embedding_model": self.model_name,
            "index_path": str(self.index_path)
        }
    
    async def clear_index(self):
        """Clear the vector index (for testing/reset)"""
        sample_doc = Document(page_content="initialization", metadata={"type": "init"})
        self.vector_store = FAISS.from_documents([sample_doc], self.embeddings)
        self.paper_metadata = {}
        self._save_index()
        self._save_metadata()
        logger.info("Cleared vector index")
