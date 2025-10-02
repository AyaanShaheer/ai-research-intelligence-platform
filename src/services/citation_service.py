import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.citation_models import (
    SourceMetadata, CitationStyle, CitationResponse,
    Author, SourceType
)

logger = logging.getLogger(__name__)

class CitationService:
    """Core citation generation service using templates"""
    
    def __init__(self):
        self.templates = self._load_templates()
        logger.info("Citation Service initialized with templates")
    
    def _load_templates(self) -> Dict:
        """Load citation templates from JSON file"""
        template_path = Path(__file__).parent.parent / "data" / "citation_templates.json"
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Citation templates file not found, using defaults")
            return {}
    
    def generate_citation(self, metadata: SourceMetadata, style: CitationStyle) -> CitationResponse:
        """Generate formatted citation"""
        try:
            # Get template for this style and source type
            template_data = self._get_template(style, metadata.source_type)
            
            if not template_data:
                raise ValueError(f"No template found for {style.value} - {metadata.source_type.value}")
            
            # Format authors
            formatted_authors = self._format_authors(metadata.authors, style)
            
            # Build citation from template
            citation = self._build_citation(metadata, template_data, formatted_authors)
            
            # Generate in-text citation
            in_text = self._generate_in_text_citation(metadata, style, template_data)
            
            # Check for missing required fields
            warnings = self._check_required_fields(metadata, template_data)
            
            return CitationResponse(
                citation=citation,
                in_text_citation=in_text,
                style=style,
                format="text",
                metadata_used=metadata.dict(),
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Citation generation error: {str(e)}")
            raise
    
    def _get_template(self, style: CitationStyle, source_type: SourceType) -> Optional[Dict]:
        """Get template for specific style and source type"""
        style_templates = self.templates.get(style.value, {})
        return style_templates.get(source_type.value)
    
    def _format_authors(self, authors: List[Author], style: CitationStyle) -> str:
        """Format author list according to citation style"""
        if not authors:
            return ""
        
        if style == CitationStyle.APA_7:
            # Last, F. M., Last2, F. M., & Last3, F. M.
            formatted = []
            for author in authors:
                initials = f"{author.first_name[0]}."
                if author.middle_name:
                    initials += f" {author.middle_name[0]}."
                formatted.append(f"{author.last_name}, {initials}")
            
            if len(formatted) == 1:
                return formatted[0]
            elif len(formatted) == 2:
                return f"{formatted[0]}, & {formatted[1]}"
            else:
                return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
        
        elif style == CitationStyle.MLA_9:
            # Last, First, and First2 Last2
            if len(authors) == 1:
                return f"{authors[0].last_name}, {authors[0].first_name}"
            elif len(authors) == 2:
                return f"{authors[0].last_name}, {authors[0].first_name}, and {authors[1].first_name} {authors[1].last_name}"
            else:
                return f"{authors[0].last_name}, {authors[0].first_name}, et al."
        
        elif style == CitationStyle.IEEE:
            # F. M. Last, F. M. Last2, and F. M. Last3
            formatted = []
            for author in authors:
                initials = f"{author.first_name[0]}."
                if author.middle_name:
                    initials += f" {author.middle_name[0]}."
                formatted.append(f"{initials} {author.last_name}")
            
            if len(formatted) <= 6:
                return ", ".join(formatted[:-1]) + f", and {formatted[-1]}" if len(formatted) > 1 else formatted[0]
            else:
                return f"{formatted[0]}, et al."
        
        else:
            # Default format
            return ", ".join([f"{a.last_name}, {a.first_name[0]}." for a in authors])
    
    def _build_citation(self, metadata: SourceMetadata, template_data: Dict, formatted_authors: str) -> str:
        """Build citation from template"""
        template = template_data.get("template", "")
        
        # Build replacement dictionary
        replacements = {
            "authors": formatted_authors,
            "year": str(metadata.year) if metadata.year else "n.d.",
            "title": self._format_title(metadata.title, template_data.get("formatting", {})),
            "journal": metadata.publication or "",
            "volume": metadata.volume or "",
            "issue": metadata.issue or "",
            "pages": metadata.pages or "",
            "doi": f"https://doi.org/{metadata.doi}" if metadata.doi else "",
            "url": metadata.url or "",
            "publisher": metadata.publisher or "",
            "edition": metadata.edition or "",
            "conference_name": metadata.conference_name or "",
        }
        
        # Replace placeholders
        citation = template
        for key, value in replacements.items():
            citation = citation.replace(f"{{{key}}}", str(value))
        
        # Clean up empty placeholders
        citation = self._clean_citation(citation)
        
        return citation
    
    def _format_title(self, title: str, formatting: Dict) -> str:
        """Format title according to style rules"""
        title_format = formatting.get("title", "")
        
        if "sentence_case" in title_format:
            # Capitalize only first word
            return title[0].upper() + title[1:].lower() if title else title
        elif "title_case" in title_format:
            # Capitalize major words
            return title.title()
        
        return title
    
    def _generate_in_text_citation(self, metadata: SourceMetadata, style: CitationStyle, template_data: Dict) -> str:
        """Generate in-text citation"""
        in_text_template = template_data.get("in_text", "")
        
        if not metadata.authors:
            author_last = "Unknown"
        else:
            author_last = metadata.authors[0].last_name
        
        replacements = {
            "author_last": author_last,
            "year": str(metadata.year) if metadata.year else "n.d.",
            "page": "",  # User would specify
            "number": ""  # For numbered styles
        }
        
        in_text = in_text_template
        for key, value in replacements.items():
            in_text = in_text.replace(f"{{{key}}}", str(value))
        
        return in_text
    
    def _check_required_fields(self, metadata: SourceMetadata, template_data: Dict) -> List[str]:
        """Check if required fields are present"""
        warnings = []
        required = template_data.get("required", [])
        
        for field in required:
            if field == "authors" and not metadata.authors:
                warnings.append("Missing required field: authors")
            elif not getattr(metadata, field, None):
                warnings.append(f"Missing recommended field: {field}")
        
        return warnings
    
    def _clean_citation(self, citation: str) -> str:
        """Clean up citation formatting"""
        # Remove empty parentheses
        citation = citation.replace("()", "")
        citation = citation.replace("(, )", "")
        
        # Remove double spaces
        while "  " in citation:
            citation = citation.replace("  ", " ")
        
        # Remove trailing punctuation duplicates
        citation = citation.replace("..", ".")
        citation = citation.replace(",,", ",")
        
        return citation.strip()
    
    def generate_bibtex(self, metadata: SourceMetadata) -> str:
        """Generate BibTeX format citation"""
        # Simplified BibTeX generation
        entry_type = self._get_bibtex_entry_type(metadata.source_type)
        cite_key = self._generate_cite_key(metadata)
        
        bibtex = f"@{entry_type}{{{cite_key},\n"
        
        if metadata.authors:
            authors_str = " and ".join([f"{a.first_name} {a.last_name}" for a in metadata.authors])
            bibtex += f"  author = {{{authors_str}}},\n"
        
        bibtex += f"  title = {{{metadata.title}}},\n"
        
        if metadata.year:
            bibtex += f"  year = {{{metadata.year}}},\n"
        
        if metadata.publication:
            bibtex += f"  journal = {{{metadata.publication}}},\n"
        
        if metadata.volume:
            bibtex += f"  volume = {{{metadata.volume}}},\n"
        
        if metadata.pages:
            bibtex += f"  pages = {{{metadata.pages}}},\n"
        
        if metadata.doi:
            bibtex += f"  doi = {{{metadata.doi}}},\n"
        
        bibtex += "}\n"
        
        return bibtex
    
    def _get_bibtex_entry_type(self, source_type: SourceType) -> str:
        """Get BibTeX entry type"""
        mapping = {
            SourceType.JOURNAL_ARTICLE: "article",
            SourceType.BOOK: "book",
            SourceType.BOOK_CHAPTER: "inbook",
            SourceType.CONFERENCE_PAPER: "inproceedings",
            SourceType.THESIS: "phdthesis",
            SourceType.REPORT: "techreport",
        }
        return mapping.get(source_type, "misc")
    
    def _generate_cite_key(self, metadata: SourceMetadata) -> str:
        """Generate BibTeX citation key"""
        if metadata.authors:
            author_last = metadata.authors[0].last_name.lower()
        else:
            author_last = "unknown"
        
        year = metadata.year or "nd"
        
        return f"{author_last}{year}"
