import arxiv
import logging
from typing import List, Optional
from datetime import datetime
from ..models.schemas import ArxivPaper, ResearchQuery

logger = logging.getLogger(__name__)

class ArxivServiceDebug:
    """Debug version of ArXiv service with extensive logging"""
    
    def __init__(self, max_results: int = 10, max_query_length: int = 300):
        self.max_results = max_results
        self.max_query_length = max_query_length
        self.client = arxiv.Client()
        logger.info(f"ArxivService initialized with max_results={max_results}")
    
    async def search_papers(self, query: ResearchQuery) -> List[ArxivPaper]:
        """Search ArXiv papers with debug logging"""
        try:
            logger.info(f"Starting search for query: '{query.query}'")
            
            # Build search query
            search_query = self._build_search_query(query.query, query.categories)
            logger.info(f"Built search query: '{search_query}'")
            
            # Create ArXiv search
            search = arxiv.Search(
                query=search_query,
                max_results=min(query.max_results, self.max_results),
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            logger.info(f"Created search object with max_results={min(query.max_results, self.max_results)}")
            
            # Process results
            papers = []
            result_count = 0
            
            for result in self.client.results(search):
                result_count += 1
                logger.info(f"Processing result {result_count}: {getattr(result, 'title', 'No title')[:50]}...")
                
                try:
                    paper = self._convert_to_paper_model(result)
                    papers.append(paper)
                    logger.info(f"Successfully converted paper {result_count}")
                except Exception as convert_error:
                    logger.error(f"Error converting result {result_count}: {str(convert_error)}")
                    continue
                
                # Limit for debugging
                if result_count >= query.max_results:
                    break
            
            logger.info(f"Successfully retrieved {len(papers)} papers out of {result_count} processed")
            return papers
            
        except Exception as e:
            logger.error(f"Error in search_papers: {str(e)}", exc_info=True)
            raise Exception(f"ArXiv search failed: {str(e)}")
    
    def _build_search_query(self, query: str, categories: Optional[List[str]] = None) -> str:
        """Build search query with logging"""
        logger.debug(f"Building query from: '{query}' with categories: {categories}")
        
        if len(query) > self.max_query_length:
            query = query[:self.max_query_length]
            logger.warning(f"Query truncated to {self.max_query_length} characters")
        
        if categories:
            category_filter = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({query}) AND ({category_filter})"
        else:
            search_query = query
            
        logger.debug(f"Final search query: '{search_query}'")
        return search_query
    
    def _convert_to_paper_model(self, arxiv_result) -> ArxivPaper:
        """Convert ArXiv result with detailed logging"""
        try:
            # Log available attributes
            logger.debug(f"Converting result with attributes: {dir(arxiv_result)}")
            
            # Extract data safely
            entry_id = getattr(arxiv_result, 'entry_id', 'unknown')
            paper_id = entry_id.split('/')[-1] if entry_id != 'unknown' else 'unknown'
            
            title = getattr(arxiv_result, 'title', 'Unknown Title')
            if hasattr(title, 'replace'):
                title = title.replace('\n', ' ').strip()
            
            authors_list = getattr(arxiv_result, 'authors', [])
            authors = [author.name if hasattr(author, 'name') else str(author) for author in authors_list]
            
            summary = getattr(arxiv_result, 'summary', 'No abstract available')
            if hasattr(summary, 'replace'):
                summary = summary.replace('\n', ' ').strip()
            
            published = getattr(arxiv_result, 'published', datetime.now())
            pdf_url = getattr(arxiv_result, 'pdf_url', '')
            categories = list(getattr(arxiv_result, 'categories', []))
            
            paper = ArxivPaper(
                id=paper_id,
                title=title,
                authors=authors,
                abstract=summary,
                published=published,
                pdf_url=pdf_url,
                categories=categories
            )
            
            logger.debug(f"Successfully created paper model for: {title[:50]}...")
            return paper
            
        except Exception as e:
            logger.error(f"Error in _convert_to_paper_model: {str(e)}", exc_info=True)
            raise
