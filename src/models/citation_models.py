from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class SourceType(str, Enum):
    """Types of sources that can be cited"""
    JOURNAL_ARTICLE = "journal_article"
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    WEBSITE = "website"
    CONFERENCE_PAPER = "conference_paper"
    THESIS = "thesis"
    REPORT = "report"
    VIDEO = "video"
    PODCAST = "podcast"
    NEWSPAPER = "newspaper"

class CitationStyle(str, Enum):
    """Supported citation styles"""
    APA_7 = "apa_7"
    MLA_9 = "mla_9"
    CHICAGO_17 = "chicago_17"
    IEEE = "ieee"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"

class Author(BaseModel):
    """Author information"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None  # Jr., Sr., III, etc.

    def get_formatted_name(self, style: CitationStyle) -> str:
        """Format author name according to citation style"""
        if style == CitationStyle.APA_7:
            # Last, F. M.
            initials = f"{self.first_name[0]}."
            if self.middle_name:
                initials += f" {self.middle_name[0]}."
            return f"{self.last_name}, {initials}"
        
        elif style == CitationStyle.MLA_9:
            # Last, First Middle
            full_name = f"{self.last_name}, {self.first_name}"
            if self.middle_name:
                full_name += f" {self.middle_name}"
            return full_name
        
        else:
            return f"{self.last_name}, {self.first_name[0]}."

class SourceMetadata(BaseModel):
    """Complete metadata for a source"""
    # Common fields
    source_type: SourceType
    title: str
    authors: List[Author] = []
    year: Optional[int] = None
    
    # Publication details
    publication: Optional[str] = None  # Journal/Publisher name
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    
    # Digital identifiers
    doi: Optional[str] = None
    url: Optional[str] = None
    access_date: Optional[str] = None
    
    # Book-specific
    edition: Optional[str] = None
    publisher: Optional[str] = None
    publisher_location: Optional[str] = None
    
    # Conference-specific
    conference_name: Optional[str] = None
    conference_location: Optional[str] = None
    
    # Thesis-specific
    institution: Optional[str] = None
    degree_type: Optional[str] = None
    
    # Media-specific
    duration: Optional[str] = None
    producer: Optional[str] = None
    
    @validator('year')
    def validate_year(cls, v):
        if v and (v < 1000 or v > datetime.now().year + 1):
            raise ValueError('Year must be between 1000 and current year')
        return v

class CitationRequest(BaseModel):
    """Request to generate a citation"""
    metadata: SourceMetadata
    style: CitationStyle
    format: str = Field(default="text", description="text, bibtex, ris, endnote")

class CitationResponse(BaseModel):
    """Response containing generated citation"""
    citation: str
    in_text_citation: str
    style: CitationStyle
    format: str
    metadata_used: Dict[str, Any]
    warnings: List[str] = []

class QuickCitationRequest(BaseModel):
    """Quick citation from natural language input"""
    text: str = Field(..., description="Natural language description of source")
    style: CitationStyle
    
class BatchCitationRequest(BaseModel):
    """Generate multiple citations at once"""
    sources: List[SourceMetadata]
    style: CitationStyle
    format: str = "text"

class DOICitationRequest(BaseModel):
    """Generate citation from DOI"""
    doi: str
    style: CitationStyle

class URLCitationRequest(BaseModel):
    """Generate citation from URL"""
    url: str
    style: CitationStyle
