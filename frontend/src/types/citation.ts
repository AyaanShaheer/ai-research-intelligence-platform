export interface Author {
  first_name: string;
  last_name: string;
  middle_name?: string;
  suffix?: string;
}

export interface SourceMetadata {
  source_type: SourceType;
  title: string;
  authors: Author[];
  year?: number | null;
  publication?: string | null;
  volume?: string | null;
  issue?: string | null;
  pages?: string | null;
  doi?: string | null;
  url?: string | null;
  publisher?: string | null;
  conference_name?: string | null;
  institution?: string | null;
  access_date?: string | null;
}

export interface Citation {
  citation: string;
  in_text_citation: string;
  style: CitationStyle;
  format: string;
  warnings?: string[];
  metadata_used?: Record<string, any>;
}

export type SourceType = 
  | 'journal_article' 
  | 'book' 
  | 'book_chapter'
  | 'website' 
  | 'conference_paper' 
  | 'thesis'
  | 'report'
  | 'video'
  | 'podcast'
  | 'newspaper';

export type CitationStyle = 
  | 'apa_7' 
  | 'mla_9' 
  | 'chicago_17' 
  | 'ieee' 
  | 'harvard' 
  | 'vancouver';
