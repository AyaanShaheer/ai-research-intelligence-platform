from typing import Dict, Any, List
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from .base_agent import BaseAgent, AgentState
from ..models.schemas import ArxivPaper
import logging

logger = logging.getLogger(__name__)

class SummarizerAgent(BaseAgent):
    """Agent responsible for summarizing research papers"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__("summarizer")
        self.llm = llm
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute summarization for retrieved papers"""
        try:
            query = state["query"]
            retrieved_papers = state.get("retrieved_papers", [])
            
            if not retrieved_papers:
                logger.warning("No papers to summarize")
                return self._create_empty_summary_result(state)
            
            # Convert papers from dict to ArxivPaper objects if needed
            papers = []
            for paper_data in retrieved_papers:
                if isinstance(paper_data, dict):
                    papers.append(ArxivPaper(**paper_data))
                else:
                    papers.append(paper_data)
            
            logger.info(f"Summarizing {len(papers)} papers for query: {query}")
            
            # Generate summary with better error handling
            try:
                summary = await self._generate_simple_summary(query, papers)
                logger.info("Summary generation successful")
            except Exception as summary_error:
                logger.error(f"Summary generation failed: {summary_error}")
                summary = self._create_manual_summary(query, papers)
            
            # Create response message
            message = AIMessage(content=summary)
            
            # Create summary data structure
            summary_data = {
                "query": query,
                "papers_count": len(papers),
                "summary": summary,
                "papers_summarized": [
                    {
                        "id": paper.id,
                        "title": paper.title,
                        "authors": paper.authors[:3],
                        "categories": paper.categories
                    }
                    for paper in papers
                ]
            }
            
            result = {
                "messages": [message],
                "summaries": [summary_data],
                "final_response": summary,
                "step": "criticism",  # Important: Set to criticism to trigger validator
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
            self.log_execution(state, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in summarizer agent: {str(e)}", exc_info=True)
            # Create a basic summary even in error case
            fallback_summary = self._create_error_summary(state.get("query", "unknown"), state.get("retrieved_papers", []))
            error_message = AIMessage(content=fallback_summary)
            return {
                "messages": [error_message],
                "summaries": [{"summary": fallback_summary, "query": state.get("query", "unknown")}],
                "final_response": fallback_summary,
                "step": "criticism",  # Still try validation even on error
                "error": str(e)
            }
    
    async def _generate_simple_summary(self, query: str, papers: List[ArxivPaper]) -> str:
        """Generate a simple summary using LLM with improved error handling"""
        try:
            # Create a more robust prompt
            papers_info = []
            for i, paper in enumerate(papers[:5], 1):  # Limit to 5 papers
                authors_str = ", ".join(paper.authors[:2])
                if len(paper.authors) > 2:
                    authors_str += " et al."
                
                # Truncate abstract to avoid token limits
                abstract = paper.abstract[:400] + "..." if len(paper.abstract) > 400 else paper.abstract
                
                paper_info = f"""
Paper {i}: {paper.title}
Authors: {authors_str}
Categories: {', '.join(paper.categories)}
Key Points: {abstract}
"""
                papers_info.append(paper_info)
            
            prompt = f"""
Research Query: "{query}"

Retrieved Papers:
{chr(10).join(papers_info)}

Please provide a comprehensive research summary that includes:

## 🎯 Overview
Brief explanation of what these papers contribute to "{query}"

## 📚 Key Findings
- Main contributions from each relevant paper
- Important methodologies or approaches
- Significant results or achievements

## 🔗 Connections
How these papers relate to each other and the query

## 💡 Research Insights
Key takeaways for someone researching "{query}"

Focus on accuracy and relevance. Be specific about what each paper contributes.
"""
            
            # Generate summary with timeout handling
            messages = [HumanMessage(content=prompt)]
            logger.info("Sending request to OpenAI for summary generation...")
            response = await self.llm.ainvoke(messages)
            
            if not response or not response.content:
                raise ValueError("Empty response from LLM")
            
            logger.info(f"Received summary of length: {len(response.content)}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in LLM summary generation: {str(e)}")
            raise  # Re-raise to trigger fallback
    
    def _create_manual_summary(self, query: str, papers: List[ArxivPaper]) -> str:
        """Create a structured manual summary when LLM fails"""
        logger.info("Creating manual summary due to LLM failure")
        
        summary_parts = [f"# Research Summary for: {query}\n"]
        summary_parts.append(f"## 📚 Found {len(papers)} Relevant Papers\n")
        
        for i, paper in enumerate(papers[:5], 1):
            authors_str = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors_str += " et al."
            
            summary_parts.append(f"### {i}. {paper.title}")
            summary_parts.append(f"**Authors:** {authors_str}")
            summary_parts.append(f"**Categories:** {', '.join(paper.categories)}")
            summary_parts.append(f"**Key Contribution:** {paper.abstract[:200]}...\n")
        
        # Add analysis section
        categories = set()
        for paper in papers:
            categories.update(paper.categories)
        
        summary_parts.append("## 🔗 Research Area Analysis")
        summary_parts.append(f"**Primary Categories:** {', '.join(list(categories)[:5])}")
        summary_parts.append(f"**Research Focus:** These papers contribute to various aspects of {query}")
        summary_parts.append("\n## 💡 Next Steps")
        summary_parts.append("- Review individual paper abstracts for detailed insights")
        summary_parts.append("- Consider the methodological approaches across papers")
        summary_parts.append("- Explore connections between different research areas")
        
        summary_parts.append("\n*Note: This summary was generated using fallback method due to system limitations.*")
        
        return "\n".join(summary_parts)
    
    def _create_error_summary(self, query: str, papers: List) -> str:
        """Create basic summary for error cases"""
        paper_count = len(papers)
        return f"""
# Research Summary for: {query}

## Status: Partial Results
Found {paper_count} papers, but summary generation encountered technical issues.

## Available Papers:
{paper_count} research papers were successfully retrieved from ArXiv.

## Recommendation:
Please review the individual paper abstracts in the response for detailed information.

*Note: AI summarization service is experiencing issues. Results show raw paper data.*
"""
    
    def _create_empty_summary_result(self, state: AgentState) -> Dict[str, Any]:
        """Create result when no papers are available"""
        query = state["query"]
        empty_message = f"No papers were found for the query: '{query}'. Please try a different search term."
        
        message = AIMessage(content=empty_message)
        
        return {
            "messages": [message],
            "summaries": [{"summary": empty_message, "query": query}],
            "final_response": empty_message,
            "step": "completed",  # Skip validation if no papers
            "iteration_count": state.get("iteration_count", 0) + 1
        }
