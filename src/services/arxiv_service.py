import arxiv
import logging
from typing import List, Optional, Union, Any
from datetime import datetime
from ..models.schemas import ArxivPaper, ResearchQuery

logger = logging.getLogger(__name__)

class ArxivService:
    """ArXiv API service for paper retrieval"""
    
    def __init__(self, max_results: int = 10, max_query_length: int = 300):
        self.max_results = max_results
        self.max_query_length = max_query_length
        self.client = arxiv.Client()
    
    async def search_papers(self, query: ResearchQuery) -> List[ArxivPaper]:
        """Search ArXiv papers based on query"""
        try:
            # Construct ArXiv search query
            search_query = self._build_search_query(query.query, query.categories)
            
            # Create ArXiv search object
            search = arxiv.Search(
                query=search_query,
                max_results=min(query.max_results, self.max_results),
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in self.client.results(search):
                paper = self._convert_to_paper_model(result)
                papers.append(paper)
                
            logger.info(f"Retrieved {len(papers)} papers for query: {query.query}")
            return papers
            
        except Exception as e:
            logger.error(f"Error searching ArXiv: {str(e)}")
            raise Exception(f"ArXiv search failed: {str(e)}")
    
    def _build_search_query(self, query: str, categories: Optional[List[str]] = None) -> str:
        """Build ArXiv search query with category filters"""
        # Truncate query if too long
        if len(query) > self.max_query_length:
            query = query[:self.max_query_length]
        
        # Add category filters if specified
        if categories:
            category_filter = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({query}) AND ({category_filter})"
        else:
            search_query = query
            
        return search_query
    
    def _convert_to_paper_model(self, arxiv_result) -> ArxivPaper:
        """Convert ArXiv result to our paper model with robust error handling"""
        try:
            return ArxivPaper(
                id=arxiv_result.entry_id.split('/')[-1],
                title=arxiv_result.title.replace('\n', ' ').strip(),
                authors=self._extract_authors(arxiv_result.authors),
                abstract=arxiv_result.summary.replace('\n', ' ').strip(),
                published=arxiv_result.published,
                pdf_url=arxiv_result.pdf_url,
                categories=[cat for cat in arxiv_result.categories]
            )
        except Exception as e:
            logger.error(f"Error converting ArXiv result to paper model: {str(e)}")
            # Return a basic paper model with available data
            return ArxivPaper(
                id=self._safe_extract_id(arxiv_result),
                title=getattr(arxiv_result, 'title', 'Unknown Title'),
                authors=self._extract_authors(getattr(arxiv_result, 'authors', [])),
                abstract=getattr(arxiv_result, 'summary', 'No abstract available'),
                published=getattr(arxiv_result, 'published', datetime.now()),
                pdf_url=getattr(arxiv_result, 'pdf_url', ''),
                categories=list(getattr(arxiv_result, 'categories', []))
            )
    
    def _extract_authors(self, authors: Any) -> List[str]:
        """Safely extract author names from various formats"""
        if not authors:
            return []
        
        author_list = []
        try:
            for author in authors:
                if hasattr(author, 'name'):
                    # ArXiv author object with .name attribute
                    author_list.append(author.name)
                elif isinstance(author, str):
                    # Direct string
                    author_list.append(author)
                else:
                    # Fallback to string conversion
                    author_list.append(str(author))
        except Exception as e:
            logger.warning(f"Error extracting authors: {e}")
            return ["Unknown Author"]
        
        return author_list
    
    def _safe_extract_id(self, arxiv_result) -> str:
        """Safely extract paper ID"""
        try:
            entry_id = getattr(arxiv_result, 'entry_id', 'unknown')
            if entry_id != 'unknown' and '/' in entry_id:
                return entry_id.split('/')[-1]
            return 'unknown'
        except Exception:
            return 'unknown'

    async def get_paper_by_id(self, paper_id: str) -> Optional[ArxivPaper]:
        """Get specific paper by ArXiv ID"""
        try:
            search = arxiv.Search(id_list=[paper_id])
            for result in self.client.results(search):
                return self._convert_to_paper_model(result)
            return None
        except Exception as e:
            logger.error(f"Error retrieving paper {paper_id}: {str(e)}")
            return None
