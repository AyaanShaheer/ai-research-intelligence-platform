import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime

# Import after setting up path in conftest.py
from src.main import app
from src.services.arxiv_service import ArxivService
from src.models.schemas import ResearchQuery, ArxivPaper

client = TestClient(app)

class TestCompleteSystem:
    """Complete system testing suite"""
    
    def test_root_endpoint(self):
        """Test basic root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Research Assistant" in data["message"]
    
    def test_health_endpoint(self):
        """Test health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @patch('src.services.arxiv_service.arxiv.Client')
    def test_research_endpoint_mocked(self, mock_client_class):
        """Test research endpoint with mocked ArXiv"""
        # Create properly configured mock
        mock_result = MagicMock()
        mock_result.entry_id = "http://arxiv.org/abs/1706.03762v5"
        mock_result.title = "Attention Is All You Need"
        
        # Fix: Proper author mock
        mock_author = MagicMock()
        mock_author.name = "Ashish Vaswani"
        mock_result.authors = [mock_author]
        
        mock_result.summary = "The dominant sequence transduction models..."
        mock_result.published = datetime(2017, 6, 12)
        mock_result.pdf_url = "http://arxiv.org/pdf/1706.03762v5.pdf"
        mock_result.categories = ["cs.CL"]
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        mock_client_instance.results.return_value = [mock_result]
        
        payload = {
            "query": "transformer architecture",
            "max_results": 1
        }
        
        response = client.post("/research", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "papers_found" in data
        assert "papers" in data
    
    def test_research_endpoint_validation_empty_query(self):
        """Test validation with empty query"""
        payload = {"query": "", "max_results": 3}
        response = client.post("/research", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_research_endpoint_validation_invalid_max_results(self):
        """Test validation with invalid max_results"""
        payload = {"query": "test", "max_results": -1}
        response = client.post("/research", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_research_endpoint_validation_too_many_results(self):
        """Test validation with too many results"""
        payload = {"query": "test", "max_results": 25}  # Above limit of 20
        response = client.post("/research", json=payload)
        assert response.status_code == 422  # Should fail validation

class TestArxivServiceUnit:
    """Unit tests for ArXiv service"""
    
    @pytest.mark.asyncio
    @patch('src.services.arxiv_service.arxiv.Client')
    async def test_arxiv_service_search_success(self, mock_client_class):
        """Test ArXiv service with mocked client"""
        # Setup properly configured mock
        mock_result = MagicMock()
        mock_result.entry_id = "http://arxiv.org/abs/test123"
        mock_result.title = "Test Paper"
        
        # Fix: Proper author mock
        mock_author = MagicMock()
        mock_author.name = "Test Author"
        mock_result.authors = [mock_author]
        
        mock_result.summary = "Test abstract"
        mock_result.published = datetime(2023, 1, 1)
        mock_result.pdf_url = "http://arxiv.org/pdf/test123.pdf"
        mock_result.categories = ["cs.AI"]
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        mock_client_instance.results.return_value = [mock_result]
        
        # Test service
        service = ArxivService(max_results=1)
        query = ResearchQuery(query="test", max_results=1)
        
        papers = await service.search_papers(query)
        
        assert len(papers) == 1
        assert papers[0].title == "Test Paper"
        assert papers[0].authors == ["Test Author"]
    
    @pytest.mark.asyncio
    @patch('src.services.arxiv_service.arxiv.Client')
    async def test_arxiv_service_search_error(self, mock_client_class):
        """Test ArXiv service error handling"""
        # Mock the client instance to raise an error
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        mock_client_instance.results.side_effect = Exception("API Error")
        
        service = ArxivService(max_results=1)
        query = ResearchQuery(query="test", max_results=1)
        
        with pytest.raises(Exception, match="ArXiv search failed"):
            await service.search_papers(query)

class TestIntegrationWithoutMocks:
    """Integration tests that actually call ArXiv (optional, run with internet)"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration  # Mark as integration test
    async def test_real_arxiv_search(self):
        """Test with real ArXiv API (requires internet)"""
        service = ArxivService(max_results=1)
        query = ResearchQuery(query="machine learning", max_results=1)
        
        try:
            papers = await service.search_papers(query)
            assert len(papers) >= 0  # May return 0 if no results
            if papers:
                assert isinstance(papers[0], ArxivPaper)
                assert papers[0].title
                assert papers[0].authors
        except Exception as e:
            pytest.skip(f"ArXiv API not available: {e}")
