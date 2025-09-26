from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from .base_agent import BaseAgent, AgentState
from ..models.schemas import ResearchQuery, ArxivPaper
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """Master coordinator agent that orchestrates the entire research pipeline"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__("coordinator")
        self.llm = llm
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Coordinate and finalize the research pipeline"""
        try:
            query = state["query"]
            retrieved_papers = state.get("retrieved_papers", [])
            summaries = state.get("summaries", [])
            validation = state.get("validation", {})
            
            logger.info(f"Coordinating final results for: {query}")
            
            # Analyze pipeline performance
            performance_analysis = self._analyze_pipeline_performance(state)
            
            # Create comprehensive final report
            final_report = await self._create_final_report(query, retrieved_papers, summaries, validation, performance_analysis)
            
            # Generate research insights
            research_insights = await self._generate_research_insights(query, retrieved_papers)
            
            # Create executive summary
            executive_summary = self._create_executive_summary(query, len(retrieved_papers), validation, performance_analysis)
            
            # Prepare metadata
            metadata = self._create_metadata(state)
            
            message = AIMessage(content=f"🎯 Research coordination completed successfully for: {query}")
            
            result = {
                "messages": [message],
                "final_response": final_report,
                "executive_summary": executive_summary,
                "research_insights": research_insights,
                "performance_analysis": performance_analysis,
                "metadata": metadata,
                "step": "completed",
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
            self.log_execution(state, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in coordinator agent: {str(e)}")
            error_message = AIMessage(content=f"Coordination error: {str(e)}")
            return {
                "messages": [error_message],
                "final_response": state.get("final_response", "Coordination failed"),
                "step": "error"
            }
    
    def _analyze_pipeline_performance(self, state: AgentState) -> Dict[str, Any]:
        """Analyze overall pipeline performance"""
        retrieved_papers = state.get("retrieved_papers", [])
        summaries = state.get("summaries", [])
        validation = state.get("validation", {})
        
        # Performance metrics
        papers_found = len(retrieved_papers)
        summary_generated = len(summaries) > 0 and bool(summaries[0].get("summary"))
        validation_passed = validation.get("overall_score", 0) >= 6
        
        # Quality assessment
        overall_score = validation.get("overall_score", "Unknown")
        confidence = validation.get("confidence", "Unknown")
        hallucination_risk = validation.get("hallucination_risk", "unknown")
        
        # Pipeline efficiency
        pipeline_steps = ["retrieval", "summarization", "validation", "coordination"]
        completed_steps = len(pipeline_steps)
        
        return {
            "papers_retrieved": papers_found,
            "summary_generated": summary_generated,
            "validation_passed": validation_passed,
            "overall_quality_score": overall_score,
            "confidence_level": confidence,
            "hallucination_risk": hallucination_risk,
            "pipeline_steps_completed": completed_steps,
            "pipeline_success_rate": "100%" if all([papers_found > 0, summary_generated, validation_passed]) else "Partial",
            "system_status": "Optimal" if validation_passed else "Review Recommended"
        }
    
    async def _create_final_report(self, query: str, papers: List, summaries: List, validation: Dict, performance: Dict) -> str:
        """Create comprehensive final research report"""
        summary_content = summaries[0].get("summary", "") if summaries else ""
        
        # Create final report structure
        report_parts = []
        
        # Header with metadata
        report_parts.append("# 📊 Research Intelligence Report")
        report_parts.append(f"**Query:** {query}")
        report_parts.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        report_parts.append(f"**Papers Analyzed:** {len(papers)}")
        report_parts.append(f"**Quality Score:** {performance.get('overall_quality_score', 'N/A')}/10")
        report_parts.append(f"**System Status:** {performance.get('system_status', 'Unknown')}\n")
        
        # Executive summary
        report_parts.append("## 🎯 Executive Summary")
        report_parts.append(f"Research analysis successfully completed with {len(papers)} relevant papers identified. "
                          f"The system achieved {performance.get('pipeline_success_rate', 'Unknown')} completion rate with "
                          f"{performance.get('confidence_level', 'moderate')} confidence level.\n")
        
        # Main research content
        report_parts.append("## 📚 Research Analysis")
        report_parts.append(summary_content)
        
        # Quality assurance section
        if validation:
            report_parts.append("\n## 🛡️ Quality Assurance")
            report_parts.append(f"- **Accuracy Assessment:** {validation.get('accuracy_score', 'N/A')}/10")
            report_parts.append(f"- **Completeness:** {validation.get('completeness_score', 'N/A')}/10")
            report_parts.append(f"- **Relevance:** {validation.get('relevance_score', 'N/A')}/10")
            report_parts.append(f"- **Hallucination Risk:** {validation.get('hallucination_risk', 'Unknown').upper()}")
        
        # System performance
        report_parts.append("\n## 📈 System Performance")
        report_parts.append(f"- **Papers Retrieved:** {performance.get('papers_retrieved', 0)}")
        report_parts.append(f"- **Pipeline Success:** {performance.get('pipeline_success_rate', 'Unknown')}")
        report_parts.append(f"- **Processing Status:** {performance.get('system_status', 'Unknown')}")
        
        report_parts.append("\n---")
        report_parts.append("*Generated by AI Research Assistant - Multi-Agent Pipeline*")
        
        return "\n".join(report_parts)
    
    async def _generate_research_insights(self, query: str, papers: List) -> List[Dict[str, Any]]:
        """Generate strategic research insights"""
        if not papers:
            return []
        
        try:
            # Extract key patterns
            categories = set()
            recent_years = 0
            authors_count = 0
            
            for paper_data in papers:
                if isinstance(paper_data, dict):
                    paper = ArxivPaper(**paper_data)
                else:
                    paper = paper_data
                
                categories.update(paper.categories)
                authors_count += len(paper.authors)
                
                # Count recent papers (2024-2025)
                if paper.published.year >= 2024:
                    recent_years += 1
            
            insights = []
            
            # Research area insight
            if categories:
                top_categories = list(categories)[:3]
                insights.append({
                    "type": "research_areas",
                    "title": "Primary Research Areas",
                    "content": f"Research spans {len(categories)} categories, primarily: {', '.join(top_categories)}",
                    "importance": "high"
                })
            
            # Recency insight
            if recent_years > 0:
                insights.append({
                    "type": "temporal_analysis", 
                    "title": "Research Recency",
                    "content": f"{recent_years}/{len(papers)} papers are from 2024-2025, indicating active research area",
                    "importance": "medium"
                })
            
            # Collaboration insight
            avg_authors = authors_count / len(papers) if papers else 0
            insights.append({
                "type": "collaboration",
                "title": "Research Collaboration",
                "content": f"Average {avg_authors:.1f} authors per paper suggests {'high' if avg_authors > 4 else 'moderate'} collaboration level",
                "importance": "medium"
            })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    def _create_executive_summary(self, query: str, papers_count: int, validation: Dict, performance: Dict) -> str:
        """Create concise executive summary"""
        quality_score = validation.get("overall_score", "Unknown")
        confidence = validation.get("confidence", "Unknown")
        
        summary = f"""
**Research Query:** {query}
**Papers Found:** {papers_count}
**Quality Assessment:** {quality_score}/10
**Confidence Level:** {confidence}%
**System Status:** {performance.get('system_status', 'Processing')}

**Key Result:** Successfully analyzed {papers_count} research papers with {'high' if isinstance(quality_score, int) and quality_score >= 7 else 'moderate'} confidence in results.
"""
        return summary.strip()
    
    def _create_metadata(self, state: AgentState) -> Dict[str, Any]:
        """Create comprehensive metadata for the research session"""
        return {
            "session_id": f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "query": state.get("query", ""),
            "papers_count": len(state.get("retrieved_papers", [])),
            "processing_time": "~30-60 seconds",  # Approximate
            "agents_used": ["retriever", "summarizer", "critic", "coordinator"],
            "pipeline_version": "1.0",
            "ai_model": "gpt-4o-mini",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
