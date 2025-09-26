from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """Application configuration"""
    
    # API Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    # ArXiv Configuration
    arxiv_max_results: int = 10
    arxiv_max_query_length: int = 300
    
    # Application Configuration
    app_name: str = "Research Assistant"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
