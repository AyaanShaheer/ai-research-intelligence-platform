import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from .agents.base_agent import AgentState
from .agents.retriever_agent import RetrieverAgent
from .agents.summarizer_agent import SummarizerAgent
from .agents.critic_agent import CriticAgent
from .agents.coordinator_agent import CoordinatorAgent
from .services.arxiv_service import ArxivService
from .models.schemas import ResearchQuery
from .config.settings import settings
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Research Intelligence Platform",
    description="Multi-Agent Research Assistant for Academic Analysis",
    version="1.0.0",
    docs_url="/api/docs",  # Move docs to /api/docs
    redoc_url="/api/redoc"
)

# Production CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://ai-research-intelligence-platform.vercel.app",
        "https://*.vercel.app",
        "https://vercel.app",
        "*" #Temporary remove after testing
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize services
arxiv_service = ArxivService(
    max_results=settings.arxiv_max_results,
    max_query_length=settings.arxiv_max_query_length
)

# Initialize LLM with error handling
try:
    llm = ChatOpenAI(
        openai_api_key=settings.openai_api_key,
        model_name=settings.openai_model,
        temperature=0.1
    )
    logger.info("OpenAI LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI LLM: {e}")
    raise

# Initialize agents
retriever_agent = RetrieverAgent(arxiv_service)
summarizer_agent = SummarizerAgent(llm)
critic_agent = CriticAgent(llm)
coordinator_agent = CoordinatorAgent(llm)

# Create workflow (your existing code)
def create_production_research_workflow():
    # Your existing workflow code here...
    async def retrieval_node(state: AgentState) -> AgentState:
        result = await retriever_agent.execute(state)
        return {**state, **result}
    
    async def summarization_node(state: AgentState) -> AgentState:
        result = await summarizer_agent.execute(state)
        return {**state, **result}
    
    async def validation_node(state: AgentState) -> AgentState:
        result = await critic_agent.execute(state)
        return {**state, **result}
    
    async def coordination_node(state: AgentState) -> AgentState:
        result = await coordinator_agent.execute(state)
        return {**state, **result}
    
    def route_after_retrieval(state: AgentState) -> str:
        if state.get("step") == "error":
            return END
        elif state.get("step") == "summarization":
            return "summarize"
        else:
            return END
    
    def route_after_summarization(state: AgentState) -> str:
        if state.get("step") == "error":
            return "coordinate"
        elif state.get("step") == "criticism":
            return "validate"
        else:
            return "coordinate"
    
    def route_after_validation(state: AgentState) -> str:
        return "coordinate"
    
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("retrieve", retrieval_node)
    graph_builder.add_node("summarize", summarization_node)
    graph_builder.add_node("validate", validation_node)
    graph_builder.add_node("coordinate", coordination_node)
    
    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_conditional_edges(
        "retrieve",
        route_after_retrieval,
        {"summarize": "summarize", END: END}
    )
    graph_builder.add_conditional_edges(
        "summarize", 
        route_after_summarization,
        {"validate": "validate", "coordinate": "coordinate"}
    )
    graph_builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {"coordinate": "coordinate"}
    )
    graph_builder.add_edge("coordinate", END)
    
    return graph_builder.compile()

research_workflow = create_production_research_workflow()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "🚀 AI Research Intelligence Platform - Production Ready!",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Research Intelligence Platform",
        "version": "1.0.0"
    }

# Your existing /research endpoint (keep as is)
@app.post("/research")
async def research_papers(query: ResearchQuery):
    try:
        logger.info(f"Research request: {query.query}")
        # Your existing research logic...
        initial_state: AgentState = {
            "messages": [],
            "query": query.query,
            "retrieved_papers": [],
            "summaries": [],
            "validation": None,
            "final_response": "",
            "step": "retrieval",
            "iteration_count": 0
        }
        
        result = await research_workflow.ainvoke(initial_state)
        
        return {
            "query": query.query,
            "executive_summary": result.get("executive_summary", ""),
            "research_report": result.get("final_response", ""),
            "research_insights": result.get("research_insights", []),
            "performance_analysis": result.get("performance_analysis", {}),
            "metadata": result.get("metadata", {}),
            "papers_analyzed": len(result.get("retrieved_papers", [])),
            "status": "success",
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Research error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system-status") 
async def system_status():
    try:
        return {
            "system_status": "operational",
            "services": {
                "arxiv_service": "operational",
                "openai_llm": "operational", 
                "multi_agent_pipeline": "operational"
            },
            "agents": {
                "retriever": "ready",
                "summarizer": "ready",
                "critic": "ready", 
                "coordinator": "ready"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"System status error: {e}")
        return {"system_status": "degraded", "error": str(e)}


#Added preflight handler
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "OK"}

@app.get("/test")
async def test_endpoints():
    return {
        "status": "working",
        "message": "Backend is accessible",
        "timestamp": "2025-09-26 20:40"
    }

# Production startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Research Intelligence Platform starting up...")
    logger.info(f"Environment: {'Production' if not settings.debug else 'Development'}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
