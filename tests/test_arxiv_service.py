import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.arxiv_service import ArxivService
from src.models.schemas import ResearchQuery

class TestArxivService:
    """Test ArxivService with proper mocking"""
    
    @pytest.fixture
    def arxiv_service(self):
        return ArxivService(max_results=5)
    
    @pytest.fixture
    def mock_arxiv_result(self):
        """Create a properly configured mock ArXiv result"""
        mock_result = MagicMock()
        mock_result.entry_id = "http://arxiv.org/abs/1706.03762v5"
        mock_result.title = "Attention Is All You Need"
        
        # Create proper author mocks
        mock_author = MagicMock()
        mock_author.name = "Ashish Vaswani"
        mock_result.authors = [mock_author]
        
        mock_result.summary = "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks"
        mock_result.published = datetime(2017, 6, 12)
        mock_result.pdf_url = "http://arxiv.org/pdf/1706.03762v5.pdf"
        mock_result.categories = ["cs.CL", "cs.AI"]
        return mock_result
    
    @pytest.mark.asyncio
    async def test_search_papers_success(self, arxiv_service, mock_arxiv_result):
        """Test successful paper search with proper mocking"""
        query = ResearchQuery(query="machine learning", max_results=1)
        
        # Mock the client instance directly on the service
        with patch.object(arxiv_service, 'client') as mock_client:
            mock_client.results.return_value = [mock_arxiv_result]
            
            papers = await arxiv_service.search_papers(query)
            
            assert isinstance(papers, list)
            assert len(papers) == 1
            assert papers[0].title == "Attention Is All You Need"
            assert papers[0].authors == ["Ashish Vaswani"]
    
    @pytest.mark.asyncio
    async def test_search_papers_error(self, arxiv_service):
        """Test error handling in paper search"""
        query = ResearchQuery(query="invalid query")
        
        # Mock the client instance to raise an error
        with patch.object(arxiv_service, 'client') as mock_client:
            mock_client.results.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="ArXiv search failed"):
                await arxiv_service.search_papers(query)
    
    def test_build_search_query(self, arxiv_service):
        """Test search query building"""
        # Test basic query
        query = arxiv_service._build_search_query("machine learning")
        assert query == "machine learning"
        
        # Test with categories
        query_with_cats = arxiv_service._build_search_query(
            "deep learning", 
            ["cs.AI", "cs.LG"]
        )
        expected = "(deep learning) AND (cat:cs.AI OR cat:cs.LG)"
        assert query_with_cats == expected
    
    def test_convert_to_paper_model(self, arxiv_service, mock_arxiv_result):
        """Test ArXiv result conversion"""
        paper = arxiv_service._convert_to_paper_model(mock_arxiv_result)
        
        assert paper.id == "1706.03762v5"
        assert paper.title == "Attention Is All You Need"
        assert paper.authors == ["Ashish Vaswani"]
        assert "cs.CL" in paper.categories
    
    def test_extract_authors_various_formats(self, arxiv_service):
        """Test author extraction with different formats"""
        # Test with mock objects having .name
        mock_author = MagicMock()
        mock_author.name = "John Doe"
        authors_with_name = arxiv_service._extract_authors([mock_author])
        assert authors_with_name == ["John Doe"]
        
        # Test with direct strings
        authors_strings = arxiv_service._extract_authors(["Jane Smith", "Bob Johnson"])
        assert authors_strings == ["Jane Smith", "Bob Johnson"]
        
        # Test with empty list
        authors_empty = arxiv_service._extract_authors([])
        assert authors_empty == []
        
        # Test with None
        authors_none = arxiv_service._extract_authors(None)
        assert authors_none == []
    
    def test_convert_to_paper_model_with_string_authors(self, arxiv_service):
        """Test conversion with string authors (error case)"""
        bad_mock = MagicMock()
        bad_mock.entry_id = "http://arxiv.org/abs/test123"
        bad_mock.title = "Test Title"
        bad_mock.authors = ["Direct String Author"]  # This should work now
        bad_mock.summary = "Test summary"
        bad_mock.published = datetime.now()
        bad_mock.pdf_url = "http://test.pdf"
        bad_mock.categories = ["cs.AI"]
        
        # This should not raise an exception
        paper = arxiv_service._convert_to_paper_model(bad_mock)
        assert paper.title == "Test Title"
        assert paper.authors == ["Direct String Author"]
    
    def test_safe_extract_id(self, arxiv_service):
        """Test safe ID extraction"""
        # Test normal case
        mock_result = MagicMock()
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678v1"
        assert arxiv_service._safe_extract_id(mock_result) == "1234.5678v1"
        
        # Test error case
        mock_bad_result = MagicMock()
        mock_bad_result.entry_id = None
        assert arxiv_service._safe_extract_id(mock_bad_result) == "unknown"
