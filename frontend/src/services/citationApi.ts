import axios, { AxiosError } from 'axios';
import { SourceMetadata, Citation, CitationStyle } from '../types/citation';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface ApiError {
  detail?: string;
  message?: string;
}

const citationApi = {
  generateCitation: async (
    metadata: SourceMetadata, 
    style: CitationStyle, 
    format: string = 'text'
  ): Promise<Citation> => {
    try {
      const response = await axios.post<Citation>(`${API_BASE_URL}/citations/generate`, {
        metadata,
        style,
        format
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to generate citation';
    }
  },

  quickGenerate: async (text: string, style: CitationStyle): Promise<Citation> => {
    try {
      const response = await axios.post<Citation>(`${API_BASE_URL}/citations/quick-generate`, {
        text,
        style
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to generate citation';
    }
  },

  generateFromDOI: async (doi: string, style: CitationStyle): Promise<Citation> => {
    try {
      const response = await axios.post<Citation>(`${API_BASE_URL}/citations/from-doi`, {
        doi,
        style
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to generate citation';
    }
  },

  generateFromURL: async (url: string, style: CitationStyle): Promise<Citation> => {
    try {
      const response = await axios.post<Citation>(`${API_BASE_URL}/citations/from-url`, {
        url,
        style
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to generate citation';
    }
  },

  batchGenerate: async (sources: SourceMetadata[], style: CitationStyle): Promise<Citation[]> => {
    try {
      const response = await axios.post<Citation[]>(`${API_BASE_URL}/citations/batch`, {
        sources,
        style
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to generate citations';
    }
  },

  getSupportedStyles: async (): Promise<Array<{code: string; name: string; description: string}>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/citations/styles`);
      return response.data.styles;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to fetch styles';
    }
  },

  getSourceTypes: async (): Promise<Array<{code: string; name: string}>> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/citations/source-types`);
      return response.data.source_types;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to fetch source types';
    }
  },

  validateCitation: async (citation: string, style: CitationStyle): Promise<{
    is_valid: boolean;
    errors: string[];
    suggestions: string[];
    corrected_citation: string;
  }> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/citations/validate`, {
        citation,
        style
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw axiosError.response?.data?.detail || axiosError.message || 'Failed to validate citation';
    }
  }
};

export default citationApi;
