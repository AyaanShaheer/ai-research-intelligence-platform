import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # App Configuration
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    app_name: str = "CiteOn AI Platform"
    version: str = "2.0.0"
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    
    # CORS Settings
    allowed_origins: list = ["*"]
    
    # FastAPI Settings
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    root_path: str = ""
    
    # Lifecycle Settings
    enable_lifespan_events: bool = False  # Disable lifespan events temporarily

# Create global settings instance
settings = Settings()

# Log configuration on import (not in __init__)
if settings.openai_api_key:
    print(f"✅ OpenAI API Key configured: {settings.openai_api_key[:10]}...")
else:
    print("⚠️  OpenAI API Key not configured")
    
if settings.gemini_api_key:
    print(f"✅ Gemini API Key configured: {settings.gemini_api_key[:10]}...")
else:
    print("⚠️  Gemini API Key not configured")