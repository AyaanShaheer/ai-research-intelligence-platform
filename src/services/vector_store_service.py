import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import uuid
import re

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Enhanced in-memory vector store with improved retrieval for RAG"""
    
    def __init__(self):
        # In-memory storage
        self.document_chunks = {}  # document_id -> List[chunk_data]
        self.chunk_vectors = {}    # chunk_id -> vector embedding
        self.all_chunks = []       # Flat list of all chunks for search
        
        logger.info("Vector Store Service initialized (in-memory) with enhanced retrieval")
    
    async def store_document_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """Store document chunks with embeddings"""
        try:
            if not chunks:
                logger.warning(f"No chunks to store for document {document_id}")
                return False
            
            stored_chunks = []
            
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())
                
                # Create simple embedding from content
                embedding = self._create_simple_embedding(chunk['content'])
                
                chunk_data = {
                    'id': chunk_id,
                    'document_id': document_id,
                    'content': chunk['content'],
                    'chunk_index': chunk.get('chunk_index', 0),
                    'metadata': chunk.get('metadata', {}),
                    'embedding': embedding,
                    'created_at': datetime.now().isoformat(),
                    'content_length': len(chunk['content']),
                    'word_count': len(chunk['content'].split())
                }
                
                stored_chunks.append(chunk_data)
                self.chunk_vectors[chunk_id] = embedding
                self.all_chunks.append(chunk_data)
            
            # Store by document ID
            if document_id in self.document_chunks:
                self.document_chunks[document_id].extend(stored_chunks)
            else:
                self.document_chunks[document_id] = stored_chunks
            
            logger.info(f"Stored {len(stored_chunks)} chunks for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing document chunks: {str(e)}")
            return False
    
    async def search_similar_chunks(self, query: str, document_ids: Optional[List[str]] = None,
                                   limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using ENHANCED retrieval strategy:
        1. Keyword matching (exact/partial text match)
        2. Semantic similarity (embedding-based)
        3. Hybrid scoring combining both approaches
        """
        try:
            # Preprocess query for better matching
            processed_query = self._preprocess_query(query)
            
            logger.info(f"Searching for: '{query}' (processed: '{processed_query}')")
            
            # Filter chunks by document IDs if provided
            searchable_chunks = []
            if document_ids:
                for doc_id in document_ids:
                    if doc_id in self.document_chunks:
                        searchable_chunks.extend(self.document_chunks[doc_id])
            else:
                searchable_chunks = self.all_chunks.copy()
            
            if not searchable_chunks:
                logger.warning(f"No chunks available to search")
                return []
            
            logger.info(f"Searching through {len(searchable_chunks)} chunks")
            
            # Create query embedding
            query_embedding = self._create_simple_embedding(processed_query)
            
            # Score all chunks using HYBRID approach
            scored_chunks = []
            for chunk in searchable_chunks:
                # 1. Semantic similarity score (embedding-based)
                semantic_score = self._cosine_similarity(
                    query_embedding,
                    chunk['embedding']
                )
                
                # 2. Keyword matching score (text-based)
                keyword_score = self._keyword_match_score(
                    processed_query,
                    chunk['content']
                )
                
                # 3. BM25-style term frequency score
                tf_score = self._term_frequency_score(
                    processed_query,
                    chunk['content']
                )
                
                # 4. Combine scores with weights (hybrid approach)
                # Give MORE weight to keyword matching for better accuracy
                final_score = (
                    0.3 * semantic_score +    # Semantic similarity
                    0.5 * keyword_score +      # Keyword matching (highest weight)
                    0.2 * tf_score            # Term frequency
                )
                
                scored_chunks.append({
                    'chunk': chunk,
                    'score': final_score,
                    'semantic_score': semantic_score,
                    'keyword_score': keyword_score,
                    'tf_score': tf_score
                })
            
            # Sort by combined score
            scored_chunks.sort(key=lambda x: x['score'], reverse=True)
            
            # Apply ADAPTIVE threshold based on top scores
            if scored_chunks:
                top_score = scored_chunks[0]['score']
                # Use 40% of top score as threshold (more lenient)
                adaptive_threshold = max(0.2, top_score * 0.4)
                
                logger.info(f"Top score: {top_score:.3f}, Adaptive threshold: {adaptive_threshold:.3f}")
                
                # Filter and return top results
                results = []
                for item in scored_chunks[:limit]:
                    if item['score'] >= adaptive_threshold:
                        chunk = item['chunk']
                        results.append({
                            'id': chunk['id'],
                            'document_id': chunk['document_id'],
                            'content': chunk['content'],
                            'chunk_index': chunk['chunk_index'],
                            'similarity_score': float(item['score']),
                            'semantic_score': float(item['semantic_score']),
                            'keyword_score': float(item['keyword_score']),
                            'metadata': chunk.get('metadata', {})
                        })
                
                logger.info(f"Found {len(results)} chunks above threshold from top {limit}")
                
                # Debug: Show top 3 scores
                for i, item in enumerate(scored_chunks[:3]):
                    logger.info(f"  Chunk {i+1}: score={item['score']:.3f} "
                              f"(sem={item['semantic_score']:.3f}, "
                              f"kw={item['keyword_score']:.3f}, "
                              f"tf={item['tf_score']:.3f})")
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching chunks: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocess query for better matching"""
        # Remove common filler words
        filler_words = ['please', 'can you', 'could you', 'tell me', 'about', 'the', 'this', 'that']
        processed = query.lower()
        
        for filler in filler_words:
            processed = processed.replace(filler, ' ')
        
        # Clean up whitespace
        processed = ' '.join(processed.split())
        
        return processed if processed else query.lower()
    
    def _keyword_match_score(self, query: str, content: str) -> float:
        """Calculate keyword matching score"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Extract keywords (words longer than 3 chars)
        query_words = set([w for w in re.findall(r'\w+', query_lower) if len(w) > 3])
        content_words = set([w for w in re.findall(r'\w+', content_lower) if len(w) > 3])
        
        if not query_words:
            return 0.0
        
        # Calculate overlap
        matching_words = query_words & content_words
        score = len(matching_words) / len(query_words)
        
        # Bonus for phrase matching
        if query_lower in content_lower:
            score += 0.5
        
        # Normalize to 0-1 range
        return min(1.0, score)
    
    def _term_frequency_score(self, query: str, content: str) -> float:
        """Calculate term frequency score (simplified BM25)"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        query_words = [w for w in re.findall(r'\w+', query_lower) if len(w) > 3]
        
        if not query_words:
            return 0.0
        
        # Count occurrences of each query word
        total_score = 0.0
        for word in query_words:
            count = content_lower.count(word)
            if count > 0:
                # TF score with diminishing returns
                tf = count / (count + 1)
                total_score += tf
        
        # Normalize by number of query words
        return min(1.0, total_score / len(query_words))
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """Create simple embedding using character and word statistics"""
        if not text:
            return np.zeros(100)
        
        text_lower = text.lower()
        
        # Character-based features (26 dimensions for a-z)
        char_freq = np.zeros(26)
        for char in text_lower:
            if 'a' <= char <= 'z':
                char_freq[ord(char) - ord('a')] += 1
        
        # Normalize character frequencies
        if char_freq.sum() > 0:
            char_freq = char_freq / char_freq.sum()
        
        # Word-based features
        words = re.findall(r'\w+', text_lower)
        word_features = np.array([
            len(words),                           # Word count
            len(text),                            # Character count
            np.mean([len(w) for w in words]) if words else 0,  # Avg word length
            len(set(words)) / max(len(words), 1), # Vocabulary diversity
        ])
        
        # Technical term indicators (presence of important keywords)
        tech_terms = [
            'model', 'method', 'result', 'data', 'algorithm', 'approach',
            'system', 'network', 'learning', 'training', 'performance',
            'transformer', 'attention', 'embedding', 'layer', 'architecture'
        ]
        tech_features = np.array([
            1.0 if term in text_lower else 0.0 for term in tech_terms[:20]
        ])
        
        # Bigram features (common word pairs)
        common_bigrams = [
            'neural network', 'machine learning', 'deep learning', 'attention mechanism',
            'sequence to', 'state of', 'we propose', 'our model', 'shows that',
            'based on', 'compared to', 'results show'
        ]
        bigram_features = np.array([
            1.0 if bigram in text_lower else 0.0 for bigram in common_bigrams[:30]
        ])
        
        # Combine all features (26 + 4 + 20 + 30 = 80 dimensions, pad to 100)
        embedding = np.concatenate([
            char_freq,          # 26 dims
            word_features,      # 4 dims
            tech_features,      # 20 dims
            bigram_features,    # 30 dims
        ])
        
        # Pad to 100 dimensions
        if len(embedding) < 100:
            embedding = np.pad(embedding, (0, 100 - len(embedding)))
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure in [0, 1] range
        return max(0.0, min(1.0, (similarity + 1) / 2))
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document"""
        return self.document_chunks.get(document_id, [])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        total_chunks = sum(len(chunks) for chunks in self.document_chunks.values())
        
        return {
            'total_documents': len(self.document_chunks),
            'total_chunks': total_chunks,
            'total_vectors': len(self.chunk_vectors),
            'avg_chunks_per_document': total_chunks / max(len(self.document_chunks), 1)
        }
