import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  Psychology,
  Speed,
  Science,
  CheckCircle,
  Schedule,
  AutoAwesome,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { researchAPI, SystemStatus } from '../services/api';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSystemStatus = async () => {
      try {
        const status = await researchAPI.getSystemStatus();
        setSystemStatus(status);
      } catch (error) {
        console.error('Failed to load system status:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSystemStatus();
  }, []);

  const features = [
    {
      title: 'Multi-Agent Pipeline',
      description: 'Coordinated AI agents working together for comprehensive research analysis',
      icon: <Psychology />,
      color: '#2196F3',
    },
    {
      title: 'Quality Assurance',
      description: 'Built-in fact-checking and validation to ensure reliable results',
      icon: <CheckCircle />,
      color: '#4CAF50',
    },
    {
      title: 'Real-time Analysis',
      description: 'Live progress tracking and instant results from ArXiv database',
      icon: <Speed />,
      color: '#FF9800',
    },
    {
      title: 'Intelligent Insights',
      description: 'AI-powered research insights and cross-paper analysis',
      icon: <AutoAwesome />,
      color: '#9C27B0',
    },
  ];

  const recentMetrics = [
    { label: 'Papers Analyzed', value: '1,247', trend: '+12%', color: 'primary' },
    { label: 'Research Queries', value: '89', trend: '+8%', color: 'secondary' },
    { label: 'Quality Score', value: '8.7/10', trend: '+0.3', color: 'success' },
    { label: 'Response Time', value: '34s', trend: '-5s', color: 'info' },
  ];

  return (
    <Box>
      {/* Welcome Section */}
      <Box display="flex" alignItems="center" mb={4}>
        <Assessment sx={{ fontSize: '3rem', mr: 2, color: 'primary.main' }} />
        <Box>
          <Typography variant="h3" component="h1" gutterBottom>
            Research Dashboard
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Welcome to your AI-powered research assistant
          </Typography>
        </Box>
      </Box>

      {/* System Status Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3, background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%)' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">System Status</Typography>
              <Chip
                label={systemStatus?.system_status === 'operational' ? '🟢 Operational' : '🟡 Loading...'}
                color={systemStatus?.system_status === 'operational' ? 'success' : 'default'}
              />
            </Box>

            {loading ? (
              <LinearProgress sx={{ mb: 2 }} />
            ) : (
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 1 }}>
                      <Science />
                    </Avatar>
                    <Typography variant="body2">ArXiv Service</Typography>
                    <Chip
                      label={systemStatus?.services?.arxiv_service || 'Unknown'}
                      size="small"
                      color={systemStatus?.services?.arxiv_service === 'operational' ? 'success' : 'warning'}
                    />
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Avatar sx={{ bgcolor: 'secondary.main', mx: 'auto', mb: 1 }}>
                      <Psychology />
                    </Avatar>
                    <Typography variant="body2">OpenAI LLM</Typography>
                    <Chip
                      label={systemStatus?.services?.openai_llm || 'Unknown'}
                      size="small"
                      color={systemStatus?.services?.openai_llm === 'operational' ? 'success' : 'warning'}
                    />
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Avatar sx={{ bgcolor: 'info.main', mx: 'auto', mb: 1 }}>
                      <Assessment />
                    </Avatar>
                    <Typography variant="body2">Multi-Agent Pipeline</Typography>
                    <Chip
                      label={systemStatus?.services?.multi_agent_pipeline || 'Unknown'}
                      size="small"
                      color={systemStatus?.services?.multi_agent_pipeline === 'operational' ? 'success' : 'warning'}
                    />
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Avatar sx={{ bgcolor: 'warning.main', mx: 'auto', mb: 1 }}>
                      <Schedule />
                    </Avatar>
                    <Typography variant="body2">Version</Typography>
                    <Chip
                      label={systemStatus?.version || '1.0.0'}
                      size="small"
                      color="info"
                    />
                  </Box>
                </Grid>
              </Grid>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Metrics */}
      <Grid container spacing={3} mb={4}>
        {recentMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card elevation={2} sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                  <Typography color="text.secondary" gutterBottom>
                    {metric.label}
                  </Typography>
                  <TrendingUp fontSize="small" color={metric.color as any} />
                </Box>
                <Typography variant="h4" component="div" color={`${metric.color}.main`}>
                  {metric.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {metric.trend} from last week
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Features Overview */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        🚀 Platform Capabilities
      </Typography>
      <Grid container spacing={3} mb={4}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card elevation={2} sx={{ height: '100%', '&:hover': { transform: 'translateY(-4px)', transition: 'transform 0.2s' } }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="flex-start" mb={2}>
                  <Avatar sx={{ bgcolor: feature.color, mr: 2 }}>
                    {feature.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          ⚡ Quick Actions
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap">
          <Button
            variant="contained"
            startIcon={<Psychology />}
            onClick={() => navigate('/research')}
            sx={{ background: 'linear-gradient(45deg, #2196F3 30%, #4CAF50 90%)' }}
          >
            Start Research
          </Button>
          <Button
            variant="outlined"
            startIcon={<Assessment />}
            onClick={() => navigate('/system')}
          >
            System Status
          </Button>
          <Button
            variant="outlined"
            startIcon={<Science />}
            disabled
          >
            Export Results
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Dashboard;
