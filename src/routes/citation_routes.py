import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models.citation_models import (
    CitationRequest, CitationResponse, QuickCitationRequest,
    BatchCitationRequest, DOICitationRequest, URLCitationRequest,
    SourceMetadata, CitationStyle
)
from ..services.citation_service import CitationService
from ..services.citation_ai_service import CitationAIService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/citations", tags=["Citations"])

# Initialize services
citation_service = CitationService()
citation_ai_service = CitationAIService()

# Dependency injection
def get_citation_service() -> CitationService:
    return citation_service

def get_citation_ai_service() -> CitationAIService:
    return citation_ai_service


@router.post("/generate", response_model=CitationResponse)
async def generate_citation(
    request: CitationRequest,
    service: CitationService = Depends(get_citation_service)
):
    """
    Generate a formatted citation from metadata
    
    Example:
    ```
    {
        "metadata": {
            "source_type": "journal_article",
            "title": "Attention Is All You Need",
            "authors": [
                {"first_name": "Ashish", "last_name": "Vaswani"}
            ],
            "year": 2017,
            "publication": "Advances in Neural Information Processing Systems",
            "volume": "30",
            "pages": "5998-6008"
        },
        "style": "apa_7",
        "format": "text"
    }
    ```
    """
    try:
        citation = service.generate_citation(request.metadata, request.style)
        
        # Handle different output formats
        if request.format == "bibtex":
            bibtex = service.generate_bibtex(request.metadata)
            citation.citation = bibtex
            citation.format = "bibtex"
        
        return citation
        
    except Exception as e:
        logger.error(f"Citation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-generate", response_model=CitationResponse)
async def quick_generate_citation(
    request: QuickCitationRequest,
    ai_service: CitationAIService = Depends(get_citation_ai_service),
    service: CitationService = Depends(get_citation_service)
):
    """
    Generate citation from natural language text using AI
    
    Example:
    ```
    {
        "text": "Cite the Attention is All You Need paper by Vaswani et al from NIPS 2017",
        "style": "apa_7"
    }
    ```
    """
    try:
        # Extract metadata using AI
        metadata = await ai_service.extract_metadata_from_text(request.text)
        
        # Generate citation
        citation = service.generate_citation(metadata, request.style)
        
        return citation
        
    except Exception as e:
        logger.error(f"Quick citation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/from-doi", response_model=CitationResponse)
async def generate_from_doi(
    request: DOICitationRequest,
    ai_service: CitationAIService = Depends(get_citation_ai_service),
    service: CitationService = Depends(get_citation_service)
):
    """
    Generate citation from DOI
    
    Example:
    ```
    {
        "doi": "10.1000/xyz123",
        "style": "apa_7"
    }
    ```
    """
    try:
        # Fetch metadata from DOI
        metadata = await ai_service.extract_metadata_from_doi(request.doi)
        
        # Generate citation
        citation = service.generate_citation(metadata, request.style)
        
        return citation
        
    except Exception as e:
        logger.error(f"DOI citation generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid DOI or API error: {str(e)}")


@router.post("/from-url", response_model=CitationResponse)
async def generate_from_url(
    request: URLCitationRequest,
    ai_service: CitationAIService = Depends(get_citation_ai_service),
    service: CitationService = Depends(get_citation_service)
):
    """
    Generate citation from URL using AI
    
    Example:
    ```
    {
        "url": "https://example.com/article",
        "style": "apa_7"
    }
    ```
    """
    try:
        # Extract metadata from URL
        metadata = await ai_service.extract_metadata_from_url(request.url)
        
        # Generate citation
        citation = service.generate_citation(metadata, request.style)
        
        return citation
        
    except Exception as e:
        logger.error(f"URL citation generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to extract metadata: {str(e)}")


@router.post("/batch", response_model=List[CitationResponse])
async def batch_generate_citations(
    request: BatchCitationRequest,
    service: CitationService = Depends(get_citation_service)
):
    """
    Generate multiple citations at once
    
    Example:
    ```
    {
        "sources": [
            {
                "source_type": "journal_article",
                "title": "Paper 1",
                "authors": [{"first_name": "John", "last_name": "Doe"}],
                "year": 2020
            },
            {
                "source_type": "book",
                "title": "Book 1",
                "authors": [{"first_name": "Jane", "last_name": "Smith"}],
                "year": 2021
            }
        ],
        "style": "apa_7"
    }
    ```
    """
    try:
        citations = []
        for metadata in request.sources:
            citation = service.generate_citation(metadata, request.style)
            citations.append(citation)
        
        return citations
        
    except Exception as e:
        logger.error(f"Batch citation generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/styles")
async def get_supported_styles():
    """Get list of supported citation styles"""
    return {
        "styles": [
            {"code": "apa_7", "name": "APA 7th Edition", "description": "American Psychological Association"},
            {"code": "mla_9", "name": "MLA 9th Edition", "description": "Modern Language Association"},
            {"code": "chicago_17", "name": "Chicago 17th Edition", "description": "Chicago Manual of Style"},
            {"code": "ieee", "name": "IEEE", "description": "Institute of Electrical and Electronics Engineers"},
            {"code": "harvard", "name": "Harvard", "description": "Harvard Referencing Style"},
            {"code": "vancouver", "name": "Vancouver", "description": "Vancouver System (ICMJE)"}
        ]
    }


@router.get("/source-types")
async def get_source_types():
    """Get list of supported source types"""
    return {
        "source_types": [
            {"code": "journal_article", "name": "Journal Article"},
            {"code": "book", "name": "Book"},
            {"code": "book_chapter", "name": "Book Chapter"},
            {"code": "website", "name": "Website"},
            {"code": "conference_paper", "name": "Conference Paper"},
            {"code": "thesis", "name": "Thesis/Dissertation"},
            {"code": "report", "name": "Technical Report"},
            {"code": "video", "name": "Video"},
            {"code": "podcast", "name": "Podcast"},
            {"code": "newspaper", "name": "Newspaper Article"}
        ]
    }


@router.post("/validate")
async def validate_citation(
    citation: str,
    style: CitationStyle,
    ai_service: CitationAIService = Depends(get_citation_ai_service)
):
    """
    Validate an existing citation
    
    Example:
    ```
    {
        "citation": "Smith, J. (2020). Title. Journal, 10(2), 123-145.",
        "style": "apa_7"
    }
    ```
    """
    try:
        validation = await ai_service.validate_citation(citation, style)
        return validation
        
    except Exception as e:
        logger.error(f"Citation validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
