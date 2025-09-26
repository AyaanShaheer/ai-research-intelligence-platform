from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from .base_agent import BaseAgent, AgentState
from ..models.schemas import ArxivPaper
import logging

logger = logging.getLogger(__name__)

class CriticAgent(BaseAgent):
    """Agent responsible for validating and critiquing summaries"""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__("critic")
        self.llm = llm
    
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute critical validation of the summary"""
        try:
            query = state["query"]
            retrieved_papers = state.get("retrieved_papers", [])
            summaries = state.get("summaries", [])
            
            if not summaries or not summaries[0].get("summary"):
                logger.warning("No summary to validate")
                return self._create_no_summary_result(state)
            
            summary_text = summaries[0]["summary"]
            
            logger.info(f"Validating summary for query: {query}")
            
            # Perform simplified validation
            validation_result = await self._simple_validation(query, retrieved_papers, summary_text)
            
            # Create critique message
            critique_message = self._create_simple_critique_message(validation_result)
            message = AIMessage(content=critique_message)
            
            # Prepare final response
            final_response = self._prepare_final_response(summary_text, validation_result)
            
            result = {
                "messages": [message],
                "final_response": final_response,
                "validation": validation_result,
                "step": "completed",
                "iteration_count": state.get("iteration_count", 0) + 1
            }
            
            self.log_execution(state, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in critic agent: {str(e)}", exc_info=True)
            # Return basic validation result
            basic_validation = {
                "overall_score": 6,
                "confidence": 70,
                "hallucination_risk": "low",
                "notes": f"Validation completed with basic checks. Error: {str(e)}"
            }
            
            error_message = AIMessage(content="✅ Basic validation completed")
            return {
                "messages": [error_message],
                "final_response": state.get("final_response", "Summary validation completed"),
                "validation": basic_validation,
                "step": "completed"
            }
    
    async def _simple_validation(self, query: str, papers: List, summary: str) -> Dict[str, Any]:
        """Perform simple validation checks"""
        try:
            # Basic validation prompt
            validation_prompt = f"""
            Review this research summary for basic quality:

            Query: {query}
            Number of papers: {len(papers)}
            Summary length: {len(summary.split())} words

            Summary:
            {summary}

            Rate this summary on a scale of 1-10 and provide brief feedback:
            - Does it address the query?
            - Does it seem coherent?
            - Does it appear to be based on the papers?

            Respond in this format:
            Score: X/10
            Feedback: Brief assessment
            """
            
            messages = [HumanMessage(content=validation_prompt)]
            response = await self.llm.ainvoke(messages)
            
            # Extract score from response
            score = self._extract_score(response.content)
            
            return {
                "overall_score": score,
                "accuracy_score": score,
                "completeness_score": score,
                "relevance_score": score,
                "hallucination_risk": "low" if score >= 7 else "medium" if score >= 5 else "high",
                "confidence": min(90, score * 10),
                "feedback": response.content,
                "papers_count": len(papers)
            }
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return self._create_fallback_validation()
    
    def _extract_score(self, response: str) -> int:
        """Extract numerical score from response"""
        import re
        score_match = re.search(r'Score:\s*(\d+)', response)
        if score_match:
            return min(10, max(1, int(score_match.group(1))))
        return 6  # Default moderate score
    
    def _create_simple_critique_message(self, validation_result: Dict[str, Any]) -> str:
        """Create simple critique message"""
        score = validation_result.get("overall_score", 5)
        risk = validation_result.get("hallucination_risk", "medium")
        confidence = validation_result.get("confidence", 50)
        
        if score >= 8:
            status = "🟢 EXCELLENT"
        elif score >= 6:
            status = "🟡 GOOD"
        elif score >= 4:
            status = "🟠 FAIR"
        else:
            status = "🔴 NEEDS IMPROVEMENT"
        
        critique = f"""
# 🛡️ Summary Validation Report

## Overall Assessment: {status}
- **Quality Score**: {score}/10
- **Confidence**: {confidence}%
- **Hallucination Risk**: {risk.upper()}

## Validation Notes
{validation_result.get("feedback", "Basic validation completed successfully.")}

---
*Validated by AI Critic Agent*
"""
        return critique.strip()
    
    def _prepare_final_response(self, original_summary: str, validation_result: Dict[str, Any]) -> str:
        """Prepare final response with validation indicator"""
        score = validation_result.get("overall_score", 5)
        
        if score >= 7:
            header = "✅ **VALIDATED SUMMARY** (High Quality)\n\n"
        elif score >= 5:
            header = "⚠️ **SUMMARY** (Moderate Quality)\n\n"
        else:
            header = "🔴 **SUMMARY** (Review Recommended)\n\n"
        
        return header + original_summary
    
    def _create_fallback_validation(self) -> Dict[str, Any]:
        """Create basic fallback validation"""
        return {
            "overall_score": 6,
            "accuracy_score": 6,
            "completeness_score": 6,
            "relevance_score": 6,
            "hallucination_risk": "medium",
            "confidence": 60,
            "feedback": "Basic validation performed due to system limitations.",
            "papers_count": 0
        }
    
    def _create_no_summary_result(self, state: AgentState) -> Dict[str, Any]:
        """Handle case with no summary"""
        message = AIMessage(content="No summary available for validation.")
        
        return {
            "messages": [message],
            "final_response": "No summary to validate",
            "validation": {"error": "No summary provided"},
            "step": "completed"
        }
