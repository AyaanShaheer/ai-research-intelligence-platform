import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Search,
  Psychology,
  Assessment,
  Speed,
  ExpandMore,
  Science,
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';
import { researchAPI, ResearchResponse, ResearchQuery } from '../services/api';

const ResearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      setError('Please enter a research query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const searchQuery: ResearchQuery = {
        query: query.trim(),
        max_results: maxResults,
      };

      console.log('🔍 Starting research:', searchQuery);
      const response = await researchAPI.conductResearch(searchQuery);
      console.log('✅ Research completed:', response);
      
      setResult(response);
    } catch (err: any) {
      console.error('❌ Research failed:', err);
      setError(err.response?.data?.detail?.message || err.message || 'Research failed');
    } finally {
      setLoading(false);
    }
  }, [query, maxResults]);

  const getQualityColor = (score: number | string) => {
    const numScore = typeof score === 'string' ? parseInt(score) || 0 : score;
    if (numScore >= 8) return 'success';
    if (numScore >= 6) return 'warning';
    return 'error';
  };

  const getQualityIcon = (score: number | string) => {
    const numScore = typeof score === 'string' ? parseInt(score) || 0 : score;
    if (numScore >= 8) return <CheckCircle />;
    if (numScore >= 6) return <Warning />;
    return <Error />;
  };

  return (
    <Box>
      {/* Page Header */}
      <Box display="flex" alignItems="center" mb={4}>
        <Search sx={{ fontSize: '2.5rem', mr: 2, color: 'primary.main' }} />
        <Box>
          <Typography variant="h3" component="h1" gutterBottom>
            AI Research Assistant
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Multi-agent system for intelligent academic research analysis
          </Typography>
        </Box>
      </Box>

      {/* Research Input */}
      <Paper elevation={3} sx={{ p: 3, mb: 4, background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%)' }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Psychology sx={{ mr: 1 }} />
          Research Query
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Enter your research question or topic"
              placeholder="e.g., transformer neural networks, quantum computing, machine learning ethics"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              variant="outlined"
              multiline
              rows={2}
              disabled={loading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  handleSearch();
                }
              }}
              sx={{ 
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                }
              }}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <Box>
              <Typography gutterBottom>Max Papers: {maxResults}</Typography>
              <Slider
                value={maxResults}
                onChange={(_, value) => setMaxResults(value as number)}
                valueLabelDisplay="auto"
                min={1}
                max={10}
                marks
                disabled={loading}
              />
            </Box>
          </Grid>
        </Grid>

        <Box display="flex" justifyContent="space-between" alignItems="center" mt={3}>
          <Box display="flex" gap={2}>
            <Chip icon={<Science />} label="ArXiv Search" size="small" />
            <Chip icon={<Psychology />} label="AI Analysis" size="small" />
            <Chip icon={<Assessment />} label="Quality Check" size="small" />
          </Box>

          <Button
            variant="contained"
            size="large"
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <Search />}
            sx={{
              px: 4,
              py: 1.5,
              background: 'linear-gradient(45deg, #2196F3 30%, #4CAF50 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #1976D2 30%, #388E3C 90%)',
              }
            }}
          >
            {loading ? 'Researching...' : 'Start Research'}
          </Button>
        </Box>

        {query && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            💡 Tip: Press Ctrl+Enter to search quickly
          </Typography>
        )}
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
          <Typography variant="body2">
            <strong>Research Error:</strong> {error}
          </Typography>
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <Paper elevation={2} sx={{ p: 4, textAlign: 'center', mb: 4 }}>
          <CircularProgress size={60} sx={{ mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            🧠 AI Agents Working...
          </Typography>
          <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
            <Chip label="🔍 Retrieving Papers" size="small" />
            <Chip label="📝 Generating Summary" size="small" />
            <Chip label="🛡️ Quality Validation" size="small" />
            <Chip label="🎯 Coordinating Results" size="small" />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            This usually takes 30-60 seconds...
          </Typography>
        </Paper>
      )}

      {/* Results */}
      {result && (
        <Grid container spacing={3}>
          {/* Performance Metrics */}
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Speed sx={{ mr: 1 }} />
                Research Performance
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="primary.main">
                      {result.papers_analyzed}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Papers Analyzed
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="secondary.main">
                      {result.processing_time}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Processing Time
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card 
                    variant="outlined" 
                    sx={{ 
                      textAlign: 'center', 
                      p: 2,
                      borderColor: `${getQualityColor(result.performance_analysis.overall_quality_score)}.main`
                    }}
                  >
                    <Box display="flex" alignItems="center" justifyContent="center" gap={1}>
                      {getQualityIcon(result.performance_analysis.overall_quality_score)}
                      <Typography variant="h4" color={`${getQualityColor(result.performance_analysis.overall_quality_score)}.main`}>
                        {result.performance_analysis.overall_quality_score}/10
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Quality Score
                    </Typography>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="h4" color="info.main">
                      {result.performance_analysis.pipeline_success_rate}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Success Rate
                    </Typography>
                  </Card>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Executive Summary */}
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                📊 Executive Summary
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                {result.executive_summary}
              </Typography>
            </Paper>
          </Grid>

          {/* Research Insights */}
          {result.research_insights && result.research_insights.length > 0 && (
            <Grid item xs={12}>
              <Paper elevation={2} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  💡 Research Insights
                </Typography>
                <Grid container spacing={2}>
                  {result.research_insights.map((insight, index) => (
                    <Grid item xs={12} md={4} key={index}>
                      <Card 
                        variant="outlined" 
                        sx={{ 
                          height: '100%',
                          borderLeft: `4px solid ${insight.importance === 'high' ? '#4CAF50' : insight.importance === 'medium' ? '#FF9800' : '#2196F3'}`
                        }}
                      >
                        <CardContent>
                          <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                            {insight.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {insight.content}
                          </Typography>
                          <Chip 
                            label={insight.importance}
                            size="small"
                            color={insight.importance === 'high' ? 'success' : insight.importance === 'medium' ? 'warning' : 'info'}
                            sx={{ mt: 1 }}
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          )}

          {/* Full Research Report */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">📚 Complete Research Report</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Paper variant="outlined" sx={{ p: 3, backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                  <Typography 
                    variant="body1" 
                    component="div"
                    sx={{ 
                      whiteSpace: 'pre-line', 
                      lineHeight: 1.8,
                      '& h1, & h2, & h3': { color: 'primary.main', mt: 2, mb: 1 },
                      '& strong': { color: 'text.primary' }
                    }}
                    dangerouslySetInnerHTML={{ 
                      __html: result.research_report.replace(/\n/g, '<br/>').replace(/##\s(.*?)(<br\/>|$)/g, '<h3 style="color: #2196F3; margin-top: 16px; margin-bottom: 8px;">$1</h3>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    }}
                  />
                </Paper>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default ResearchPage;
