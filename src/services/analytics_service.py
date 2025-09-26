import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..models.usage_models import UsageEvent, WorkspaceUsage

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Enterprise analytics and insights service"""
    
    def __init__(self):
        self.usage_events = []  # In production: use database
        self.workspace_analytics = {}
    
    def track_research_query(self, workspace_id: str, user_email: str, 
                           query: str, papers_found: int, processing_time: float,
                           quality_score: float) -> None:
        """Track research query for analytics"""
        event = UsageEvent(
            workspace_id=workspace_id,
            user_email=user_email,
            event_type="research_query",
            tokens_used=len(query.split()) * 4,  # Rough token estimate
            processing_time=processing_time,
            quality_score=quality_score,
            timestamp=datetime.utcnow(),
            metadata={
                "query": query,
                "papers_found": papers_found,
                "query_length": len(query)
            }
        )
        self.usage_events.append(event)
    
    def get_workspace_analytics(self, workspace_id: str) -> Dict[str, Any]:
        """Generate comprehensive workspace analytics"""
        workspace_events = [e for e in self.usage_events if e.workspace_id == workspace_id]
        
        if not workspace_events:
            return {"error": "No usage data available"}
        
        total_queries = len([e for e in workspace_events if e.event_type == "research_query"])
        avg_quality = sum(e.quality_score or 0 for e in workspace_events) / len(workspace_events)
        avg_processing_time = sum(e.processing_time for e in workspace_events) / len(workspace_events)
        total_papers = sum(e.metadata.get("papers_found", 0) for e in workspace_events)
        
        # Research trends
        last_7_days = datetime.utcnow() - timedelta(days=7)
        recent_events = [e for e in workspace_events if e.timestamp >= last_7_days]
        
        return {
            "workspace_id": workspace_id,
            "total_research_queries": total_queries,
            "total_papers_analyzed": total_papers,
            "average_quality_score": round(avg_quality, 2),
            "average_processing_time": round(avg_processing_time, 2),
            "queries_last_7_days": len(recent_events),
            "research_efficiency": "High" if avg_quality > 7 else "Medium" if avg_quality > 5 else "Needs Improvement",
            "top_research_areas": self._get_top_research_areas(workspace_events),
            "usage_trends": self._get_usage_trends(workspace_events)
        }
    
    def _get_top_research_areas(self, events: List[UsageEvent]) -> List[str]:
        """Extract top research areas from queries"""
        queries = [e.metadata.get("query", "") for e in events]
        # Simple keyword extraction (in production: use NLP)
        common_words = ["machine learning", "neural networks", "AI", "deep learning", "transformer"]
        area_counts = {}
        
        for query in queries:
            query_lower = query.lower()
            for area in common_words:
                if area in query_lower:
                    area_counts[area] = area_counts.get(area, 0) + 1
        
        return sorted(area_counts.keys(), key=lambda x: area_counts[x], reverse=True)[:5]
    
    def _get_usage_trends(self, events: List[UsageEvent]) -> Dict[str, Any]:
        """Analyze usage trends"""
        if len(events) < 2:
            return {"trend": "insufficient_data"}
        
        # Simple trend analysis
        recent_half = events[len(events)//2:]
        older_half = events[:len(events)//2]
        
        recent_avg_quality = sum(e.quality_score or 0 for e in recent_half) / len(recent_half)
        older_avg_quality = sum(e.quality_score or 0 for e in older_half) / len(older_half)
        
        quality_trend = "improving" if recent_avg_quality > older_avg_quality else "declining"
        
        return {
            "quality_trend": quality_trend,
            "usage_frequency": "increasing" if len(recent_half) > len(older_half) else "stable"
        }
