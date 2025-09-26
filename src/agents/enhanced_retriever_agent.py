from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from .base_agent import BaseAgent, AgentState
from ..services.arxiv_service import ArxivService
from ..services.vector_store_service import VectorStoreService
from ..models.schemas import ResearchQuery, VectorSearchResult

class EnhancedRetrieverAgent(BaseAgent):
    """Enhanced retriever agent with vector search capabilities"""
    
    def __init__(self, 
                 arxiv_service: ArxivService,
                 vector_service: VectorStoreService):
        super().__init__("enhanced_retriever")
        self.arxiv_service = arxiv_service
        self.vector_service = vector_service
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute enhanced retrieval with both keyword and vector search"""
        try:
            query = state["query"]
            self.logger.info(f"Enhanced retrieval for: {query}")
            
            # Create research query object
            research_query = ResearchQuery(
                query=query, 
                max_results=5,
                use_vector_search=True,
                similarity_threshold=0.3
            )
            
            # Step 1: Retrieve new papers from ArXiv
            self.logger.info("Fetching fresh papers from ArXiv...")
            fresh_papers = await self.arxiv_service.search_papers(research_query)
            
            # Step 2: Add new papers to vector index
            if fresh_papers:
                self.logger.info(f"Adding {len(fresh_papers)} papers to vector index...")
                added_count = await self.vector_service.add_papers_to_index(fresh_papers)
                self.logger.info(f"Added {added_count} new papers to index")
            
            # Step 3: Perform semantic search
            self.logger.info("Performing semantic search...")
            vector_results = await self.vector_service.semantic_search(
                query=query,
                k=8,  # Get more results for better selection
                similarity_threshold=research_query.similarity_threshold
            )
            
            # Step 4: Combine and deduplicate results
            final_papers = self._combine_and_rank_results(fresh_papers, vector_results)
            
            # Step 5: Create response message
            message_content = self._create_summary_message(query, final_papers, vector_results)
            message = AIMessage(content=message_content)
            
            # Prepare result
            result = {
                "messages": [message],
                "retrieved_papers": [paper.model_dump() for paper in final_papers],
                "vector_results": [result.model_dump() for result in vector_results[:5]],
                "step": "summarization",
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
            self.log_execution(state, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in enhanced retriever agent: {str(e)}")
            error_message = AIMessage(content=f"Error in enhanced retrieval: {str(e)}")
            return {
                "messages": [error_message],
                "retrieved_papers": [],
                "vector_results": [],
                "step": "error"
            }
    
    def _combine_and_rank_results(self, 
                                fresh_papers: List,
                                vector_results: List[VectorSearchResult]) -> List:
        """Combine and rank papers from different sources"""
        paper_dict = {}
        
        # Add fresh papers (highest priority for recency)
        for paper in fresh_papers:
            paper_dict[paper.id] = {
                'paper': paper,
                'score': 1.0,  # Max score for fresh papers
                'source': 'arxiv_fresh'
            }
        
        # Add vector search results (prioritize by similarity score)
        for result in vector_results:
            if result.paper.id not in paper_dict:
                paper_dict[result.paper.id] = {
                    'paper': result.paper,
                    'score': result.similarity_score * 0.9,  # Slightly lower than fresh
                    'source': 'vector_search'
                }
            else:
                # If paper exists, boost score
                paper_dict[result.paper.id]['score'] = min(1.0, 
                    paper_dict[result.paper.id]['score'] + result.similarity_score * 0.2)
        
        # Sort by score and return top papers
        sorted_papers = sorted(
            paper_dict.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        # Return top 8 papers
        final_papers = [item['paper'] for item in sorted_papers[:8]]
        self.logger.info(f"Combined results: {len(final_papers)} unique papers")
        
        return final_papers
    
    def _create_summary_message(self, 
                              query: str, 
                              papers: List, 
                              vector_results: List[VectorSearchResult]) -> str:
        """Create informative summary message"""
        fresh_count = len([p for p in papers if any(vr.paper.id == p.id for vr in vector_results) == False])
        vector_count = len(vector_results)
        
        summary = f"🔍 Enhanced search results for '{query}':\n\n"
        summary += f"📚 Found {len(papers)} relevant papers:\n"
        summary += f"  • {fresh_count} fresh papers from ArXiv\n"
        summary += f"  • {vector_count} semantically similar papers from index\n\n"
        
        # Show top 3 papers
        summary += "📖 Top Results:\n"
        for i, paper in enumerate(papers[:3], 1):
            authors_str = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors_str += f" et al."
            summary += f"{i}. {paper.title}\n   by {authors_str}\n"
            
            # Show relevance if from vector search
            matching_vector_result = next(
                (vr for vr in vector_results if vr.paper.id == paper.id), 
                None
            )
            if matching_vector_result:
                summary += f"   📊 Similarity: {matching_vector_result.similarity_score:.2f}\n"
            summary += "\n"
        
        return summary
