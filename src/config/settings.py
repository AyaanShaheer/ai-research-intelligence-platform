import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ArXiv Configuration
    arxiv_max_results: int = 20
    arxiv_max_query_length: int = 500
    
    # OpenAI Configuration  
    openai_model: str = "gpt-4o-mini"
    
    class Config:
        case_sensitive = False

settings = Settings()
