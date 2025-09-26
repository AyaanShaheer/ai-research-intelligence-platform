from typing import Dict, Any
from langchain_core.messages import AIMessage
from .base_agent import BaseAgent, AgentState
from ..services.arxiv_service import ArxivService
from ..models.schemas import ResearchQuery

class RetrieverAgent(BaseAgent):
    """Agent responsible for retrieving research papers"""
    
    def __init__(self, arxiv_service: ArxivService):
        super().__init__("retriever")
        self.arxiv_service = arxiv_service
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve papers based on the query"""
        try:
            query = state["query"]
            self.logger.info(f"Retrieving papers for: {query}")
            
            # Create research query object
            research_query = ResearchQuery(query=query, max_results=5)
            
            # Search for papers
            papers = await self.arxiv_service.search_papers(research_query)
            
            # Create message for conversation history
            papers_summary = f"Retrieved {len(papers)} papers:\n"
            for i, paper in enumerate(papers[:3], 1):  # Show first 3
                papers_summary += f"{i}. {paper.title} by {', '.join(paper.authors[:2])}\n"
            
            message = AIMessage(content=papers_summary)
            
            result = {
                "messages": [message],
                "retrieved_papers": [paper.model_dump() for paper in papers],  # Fixed: Use model_dump()
                "step": "summarization",
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
            self.log_execution(state, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in retriever agent: {str(e)}")
            error_message = AIMessage(content=f"Error retrieving papers: {str(e)}")
            return {
                "messages": [error_message],
                "retrieved_papers": [],
                "step": "error"
            }
