from typing import Dict, Any, TypedDict, Annotated, Sequence
from abc import ABC, abstractmethod
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
import logging

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Shared state between agents in LangGraph"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str
    retrieved_papers: list
    summaries: list
    final_response: str
    step: str
    iteration_count: int

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute agent's primary function"""
        pass
    
    def should_continue(self, state: AgentState) -> bool:
        """Determine if agent should continue processing"""
        return state.get("iteration_count", 0) < 3
    
    def log_execution(self, state: AgentState, result: Dict[str, Any]):
        """Log agent execution for debugging"""
        self.logger.info(f"Agent {self.name} executed for query: {state.get('query', 'Unknown')}")
        self.logger.debug(f"Result keys: {list(result.keys())}")
