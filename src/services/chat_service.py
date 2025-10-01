import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import asyncio
import re
import openai
import os 

from .vector_store_service import VectorStoreService

openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger(__name__)

class ChatService:
    """RAG-powered chat service for document Q&A with improved response generation"""
    
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        
        # In-memory chat session storage
        self.chat_sessions = {}  # session_id -> session_data
        self.chat_messages = {}  # session_id -> List[messages]
        
        logger.info("Chat Service initialized with improved response generation")
    
    async def start_chat_session(self, document_ids: List[str], 
                                session_name: Optional[str] = None) -> str:
        """Start a new chat session with specific documents"""
        try:
            session_id = str(uuid.uuid4())
            
            session_data = {
                'id': session_id,
                'name': session_name or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'document_ids': document_ids,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'message_count': 0
            }
            
            self.chat_sessions[session_id] = session_data
            self.chat_messages[session_id] = []
            
            logger.info(f"Started chat session {session_id} with {len(document_ids)} documents")
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting chat session: {str(e)}")
            raise
    
    async def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Send a message and get AI response"""
        try:
            if session_id not in self.chat_sessions:
                raise ValueError(f"Chat session {session_id} not found")
            
            session = self.chat_sessions[session_id]
            
            # Store user message
            user_message = {
                'id': str(uuid.uuid4()),
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat(),
                'sources': []
            }
            
            # Search for relevant chunks
            relevant_chunks = await self.vector_store.search_similar_chunks(
                query=message,
                document_ids=session['document_ids'],
                limit=3
            )
            
            logger.info(f"Found {len(relevant_chunks)} relevant chunks for query: '{message}'")
            
            # Generate AI response based on relevant chunks
            ai_response, sources = await self._generate_intelligent_response(message, relevant_chunks)
            
            # Store AI message
            ai_message = {
                'id': str(uuid.uuid4()),
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now().isoformat(),
                'sources': sources
            }
            
            # Add messages to session
            if session_id not in self.chat_messages:
                self.chat_messages[session_id] = []
            
            self.chat_messages[session_id].extend([user_message, ai_message])
            
            # Update session metadata
            session['last_activity'] = datetime.now().isoformat()
            session['message_count'] += 2
            
            logger.info(f"Generated response in session {session_id} with {len(sources)} sources")
            
            return {
                'user_message': user_message,
                'ai_message': ai_message,
                'sources_count': len(sources),
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
    
    async def _generate_intelligent_response(self, query: str, relevant_chunks: list) -> tuple:
        if not relevant_chunks:
            return self._generate_no_context_response(query), []
        
        #Combine retrieved chunks as context
        docs = [chunk['content'] for chunk in relevant_chunks]
        context = "\n\n".join(docs)[:3500] #Limit context for token safety

        system_prompt = (
            "You are a research assistant. Only use the provided CONTEXT to answer questions. " 
            "If the answer is not directly in the CONTEXT, reply: 'This document does not contain that information.'"
        )
        messages = [
        {"role": "system", "content": f"{system_prompt}\n\nCONTEXT:\n{context}"},
        {"role": "user", "content": query}
    ]
        #openai call 
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=512,
                temperature=0.2
            )
        )

        answer = result.choices[0].message.content
        sources = [{
        "chunk_id": chunk.get("id", ""),
        "document_id": chunk.get("document_id", ""),
        "similarity_score": chunk.get("similarity_score", 0),
        "chunk_index": chunk.get("chunk_index", 0),
        "content_preview": chunk["content"][:120]
        } for chunk in relevant_chunks]

        return answer, sources

    def _clean_chunk_content(self, content: str) -> str:
        """Clean chunk content to remove noise and artifacts"""
        if not content:
            return ""
        
        # Remove email addresses
        content = re.sub(r'\S+@\S+\.\S+', '', content)
        
        # Remove author attribution patterns and symbols
        content = re.sub(r'[A-Z][a-z]+\s*[‡†*★]+[^a-zA-Z]*[A-Z][a-z]*', '', content)
        content = re.sub(r'[‡†*★▲]+\s*[A-Z][a-z]+\s+[A-Z][a-z]+', '', content)
        content = re.sub(r'University\s+of\s+[A-Z][a-z]+[^.]*', '', content)
        
        # Remove table references and numbers that are artifacts
        content = re.sub(r'Table\s+\d+[:.]?[^.]*\.?', 'Table reference.', content)
        content = re.sub(r'\d+\s*\.\s*\d+\s*\d*', '', content)  # Remove floating point numbers
        
        # Remove isolated symbols and characters
        content = re.sub(r'\s+[‡†*+★▲]\s+', ' ', content)
        content = re.sub(r'\s+[‡†*+★▲]+\s*$', '', content)
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove lines that are mostly metadata
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines with too many symbols or very short
            if len(line) > 15 and len(re.findall(r'[a-zA-Z]', line)) / len(line) > 0.7:
                # Skip lines that are mostly author names and affiliations
                if not re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+.*[‡†*★]', line):
                    clean_lines.append(line)
        
        cleaned = '\n'.join(clean_lines).strip()
        
        # Final cleanup of remaining artifacts
        cleaned = re.sub(r'^[^a-zA-Z]*', '', cleaned)  # Remove leading non-letters
        cleaned = re.sub(r'[‡†*★▲]+.*$', '', cleaned)  # Remove trailing artifacts
        
        return cleaned


    
    def _generate_contextual_response(self, query: str, clean_contents: List[str]) -> str:
        """Generate response based on query and cleaned content"""
        
        query_lower = query.lower()
        
        # Combine clean content
        combined_content = ' '.join(clean_contents)
        
        # Determine response type based on query
        if any(word in query_lower for word in ['summarize', 'summary', 'what is this', 'about this', 'tell me about']):
            return self._generate_summary_response(combined_content)
        elif any(word in query_lower for word in ['how', 'method', 'approach', 'technique']):
            return self._generate_methodology_response(query, combined_content)
        elif any(word in query_lower for word in ['what', 'define', 'explain']):
            return self._generate_explanation_response(query, combined_content)
        elif any(word in query_lower for word in ['why', 'reason', 'purpose']):
            return self._generate_reasoning_response(query, combined_content)
        elif any(word in query_lower for word in ['result', 'finding', 'conclusion']):
            return self._generate_findings_response(combined_content)
        else:
            return self._generate_general_response(query, combined_content)
    
    def _generate_summary_response(self, content: str) -> str:
        """Generate a summary response"""
        # Extract key sentences that seem to be main points
        sentences = [s.strip() + '.' for s in content.split('.') if s.strip()]
        
        # Look for sentences with key academic terms
        key_terms = ['paper', 'model', 'approach', 'method', 'result', 'propose', 'present', 'introduce', 'achieve', 'show']
        important_sentences = []
        
        for sentence in sentences[:10]:  # Look at first 10 sentences
            if len(sentence) > 30 and any(term in sentence.lower() for term in key_terms):
                important_sentences.append(sentence)
            if len(important_sentences) >= 3:  # Limit to 3 key sentences
                break
        
        if important_sentences:
            summary = ' '.join(important_sentences[:2])  # Use top 2 sentences
        else:
            # Fallback: use first meaningful sentences
            meaningful_sentences = [s for s in sentences if len(s) > 50][:2]
            summary = ' '.join(meaningful_sentences)
        
        return f"""Based on your document, here's a summary:

{summary}

Would you like me to elaborate on any specific aspect?"""
    
    def _generate_methodology_response(self, query: str, content: str) -> str:
        """Generate methodology-focused response"""
        # Look for methodology-related content
        sentences = content.split('.')
        method_sentences = []
        
        method_keywords = ['method', 'approach', 'algorithm', 'technique', 'process', 'procedure', 'architecture', 'model', 'framework']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in method_keywords):
                if len(sentence.strip()) > 30:
                    method_sentences.append(sentence.strip())
            if len(method_sentences) >= 2:
                break
        
        if method_sentences:
            response_content = '. '.join(method_sentences) + '.'
        else:
            # Fallback to general content
            response_content = '. '.join([s.strip() for s in sentences[:2] if s.strip()]) + '.'
        
        return f"""Regarding the methodology in your question "{query}":

{response_content}

Is there a specific methodological aspect you'd like me to explain further?"""
    
    def _generate_explanation_response(self, query: str, content: str) -> str:
        """Generate explanation-type response"""
        # Extract explanatory content
        sentences = [s.strip() for s in content.split('.') if s.strip() and len(s.strip()) > 20]
        
        # Select most relevant sentences (first 2-3 meaningful ones)
        relevant_content = '. '.join(sentences[:2]) + '.' if sentences else content[:300]
        
        return f"""Based on your document, here's what I found regarding "{query}":

{relevant_content}

Would you like me to provide more details on any particular point?"""
    
    def _generate_reasoning_response(self, query: str, content: str) -> str:
        """Generate reasoning/why-type response"""
        # Look for causal or explanatory phrases
        sentences = content.split('.')
        reasoning_sentences = []
        
        reasoning_keywords = ['because', 'since', 'due to', 'reason', 'cause', 'therefore', 'thus', 'hence', 'as a result']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in reasoning_keywords):
                if len(sentence.strip()) > 30:
                    reasoning_sentences.append(sentence.strip())
            if len(reasoning_sentences) >= 2:
                break
        
        if reasoning_sentences:
            response_content = '. '.join(reasoning_sentences) + '.'
        else:
            response_content = '. '.join([s.strip() for s in sentences[:2] if s.strip()]) + '.'
        
        return f"""Regarding your question "{query}":

{response_content}

Would you like me to explore this reasoning further?"""
    
    def _generate_findings_response(self, content: str) -> str:
        """Generate findings/results response"""
        sentences = content.split('.')
        findings_sentences = []
        
        findings_keywords = ['result', 'finding', 'conclusion', 'achieve', 'demonstrate', 'show', 'prove', 'indicate', 'reveal']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in findings_keywords):
                if len(sentence.strip()) > 30:
                    findings_sentences.append(sentence.strip())
            if len(findings_sentences) >= 2:
                break
        
        if findings_sentences:
            response_content = '. '.join(findings_sentences) + '.'
        else:
            response_content = '. '.join([s.strip() for s in sentences[:2] if s.strip()]) + '.'
        
        return f"""Here are the key findings from your document:

{response_content}

Would you like me to explain any of these results in more detail?"""
    
    def _generate_general_response(self, query: str, content: str) -> str:
        """Generate general response"""
        # Extract first meaningful paragraph or sentences
        sentences = [s.strip() for s in content.split('.') if s.strip() and len(s.strip()) > 30][:2]
        response_content = '. '.join(sentences) + '.' if sentences else content[:300]
        
        return f"""Based on your document regarding "{query}":

{response_content}

Please let me know if you'd like more specific information about any aspect!"""
    
    def _generate_no_context_response(self, query: str) -> str:
        """Generate response when no relevant context is found"""
        return f"""I couldn't find specific information in your uploaded document(s) that directly answers your question: "{query}".

This could mean:
• The information might not be present in the uploaded documents
• Try rephrasing your question or asking about topics covered in your documents
• Ask more general questions about the document's main themes

Would you like to try asking your question differently, or would you like me to tell you what topics are covered in your documents?"""
    
    async def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        try:
            return self.chat_messages.get(session_id, [])
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    async def get_chat_sessions(self) -> List[Dict[str, Any]]:
        """Get all chat sessions"""
        try:
            return list(self.chat_sessions.values())
        except Exception as e:
            logger.error(f"Error getting chat sessions: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chat service statistics"""
        total_messages = sum(len(messages) for messages in self.chat_messages.values())
        
        return {
            'total_sessions': len(self.chat_sessions),
            'total_messages': total_messages,
            'active_sessions': len([s for s in self.chat_sessions.values() if s['message_count'] > 0])
        }
