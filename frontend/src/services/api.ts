import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://ai-research-intelligence-platform.onrender.com'  // Update with your Railway URL
  : '/api';

// Configure axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for research operations
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false  
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Enhanced error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Success: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`❌ API Error: ${error.response.status} ${error.response.config.url}`);
      console.error('Response data:', error.response.data);
    } else if (error.request) {
      console.error('❌ Network Error: No response received');
      console.error('Request:', error.request);
    } else {
      console.error('❌ Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);



// Test endpoint
export const testAPI = {
  async testConnection(): Promise<any> {
    try {
      const response = await api.get('/test');
      return response.data;
    } catch (error) {
      console.error('Test connection failed:', error);
      throw error;
    }
  }
};

// API Types
export interface ResearchQuery {
  query: string;
  max_results?: number;
}

export interface ResearchResponse {
  query: string;
  executive_summary: string;
  research_report: string;
  research_insights: ResearchInsight[];
  performance_analysis: PerformanceAnalysis;
  metadata: Metadata;
  papers_analyzed: number;
  processing_time: string;
  status: string;
  version: string;
}

export interface ResearchInsight {
  type: string;
  title: string;
  content: string;
  importance: string;
}

export interface PerformanceAnalysis {
  papers_retrieved: number;
  summary_generated: boolean;
  validation_passed: boolean;
  overall_quality_score: number | string;
  confidence_level: number | string;
  hallucination_risk: string;
  pipeline_success_rate: string;
  system_status: string;
}

export interface Metadata {
  session_id: string;
  timestamp: string;
  agents_used: string[];
  ai_model: string;
  status: string;
}

export interface SystemStatus {
  system_status: string;
  services: {
    arxiv_service: string;
    openai_llm: string;
    multi_agent_pipeline: string;
  };
  agents: {
    retriever: string;
    summarizer: string;
    critic: string;
    coordinator: string;
  };
  capabilities: string[];
  version: string;
  timestamp: string;
}

// API Functions
export const researchAPI = {
  // Conduct research
  async conductResearch(query: ResearchQuery): Promise<ResearchResponse> {
    try {
      const response = await api.post<ResearchResponse>('/research', query);
      return response.data;
    } catch (error) {
      console.error('Research API Error:', error);
      throw error;
    }
  },

  // Get system status
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response = await api.get<SystemStatus>('/system-status');
      return response.data;
    } catch (error) {
      console.error('System Status API Error:', error);
      throw error;
    }
  },

  // Health check
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health Check API Error:', error);
      throw error;
    }
  },
};

export default api;
