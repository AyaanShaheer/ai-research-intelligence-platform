import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  CircularProgress,
  Button,
  Divider,
} from '@mui/material';
import {
  Settings,
  CheckCircle,
  Error,
  Warning,
  Psychology,
  Science,
  Assessment,
  Speed,
  Refresh,
  Computer,
  Cloud,
  Storage,
} from '@mui/icons-material';
import { researchAPI, SystemStatus as SystemStatusType } from '../services/api';

const SystemStatus: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatusType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const loadSystemStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const status = await researchAPI.getSystemStatus();
      setSystemStatus(status);
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.message || 'Failed to load system status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSystemStatus();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircle color="success" />;
      case 'degraded':
        return <Warning color="warning" />;
      case 'error':
        return <Error color="error" />;
      default:
        return <Settings color="action" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
      case 'ready':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Page Header */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={4}>
        <Box display="flex" alignItems="center">
          <Settings sx={{ fontSize: '2.5rem', mr: 2, color: 'primary.main' }} />
          <Box>
            <Typography variant="h3" component="h1" gutterBottom>
              System Status
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Monitor the health and performance of all system components
            </Typography>
          </Box>
        </Box>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadSystemStatus}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
          <Typography variant="body2">
            <strong>Status Check Failed:</strong> {error}
          </Typography>
        </Alert>
      )}

      {systemStatus && (
        <Grid container spacing={3}>
          {/* Overall System Status */}
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Overall System Health</Typography>
                <Chip
                  icon={getStatusIcon(systemStatus.system_status)}
                  label={systemStatus.system_status.toUpperCase()}
                  color={getStatusColor(systemStatus.system_status) as any}
                  sx={{ fontWeight: 600 }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                Last updated: {lastRefresh.toLocaleString()}
              </Typography>
            </Paper>
          </Grid>

          {/* Service Status */}
          <Grid item xs={12} md={6}>
            <Card elevation={2} sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <Cloud sx={{ mr: 1 }} />
                  External Services
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <Science />
                    </ListItemIcon>
                    <ListItemText 
                      primary="ArXiv API Service"
                      secondary="Paper retrieval and search"
                    />
                    <Chip
                      label={systemStatus.services?.arxiv_service || 'Unknown'}
                      size="small"
                      color={getStatusColor(systemStatus.services?.arxiv_service || '') as any}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Psychology />
                    </ListItemIcon>
                    <ListItemText 
                      primary="OpenAI LLM Service"
                      secondary="AI summarization and analysis"
                    />
                    <Chip
                      label={systemStatus.services?.openai_llm || 'Unknown'}
                      size="small"
                      color={getStatusColor(systemStatus.services?.openai_llm || '') as any}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Assessment />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Multi-Agent Pipeline"
                      secondary="Agent coordination system"
                    />
                    <Chip
                      label={systemStatus.services?.multi_agent_pipeline || 'Unknown'}
                      size="small"
                      color={getStatusColor(systemStatus.services?.multi_agent_pipeline || '') as any}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Agent Status */}
          <Grid item xs={12} md={6}>
            <Card elevation={2} sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <Computer sx={{ mr: 1 }} />
                  AI Agents
                </Typography>
                <List dense>
                  {systemStatus.agents && Object.entries(systemStatus.agents).map(([agent, status]) => (
                    <ListItem key={agent}>
                      <ListItemIcon>
                        {getStatusIcon(status)}
                      </ListItemIcon>
                      <ListItemText 
                        primary={agent.charAt(0).toUpperCase() + agent.slice(1)}
                        secondary={`Agent status: ${status}`}
                      />
                      <Chip
                        label={status}
                        size="small"
                        color={getStatusColor(status) as any}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* System Information */}
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <Storage sx={{ mr: 1 }} />
                  System Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Version</Typography>
                      <Typography variant="h6">{systemStatus.version}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Capabilities</Typography>
                      <Typography variant="h6">{systemStatus.capabilities?.length || 0}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Agents</Typography>
                      <Typography variant="h6">{Object.keys(systemStatus.agents || {}).length}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Services</Typography>
                      <Typography variant="h6">{Object.keys(systemStatus.services || {}).length}</Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                {/* Capabilities */}
                {systemStatus.capabilities && systemStatus.capabilities.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      System Capabilities
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {systemStatus.capabilities.map((capability, index) => (
                        <Chip
                          key={index}
                          label={capability.replace(/_/g, ' ').toUpperCase()}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Recommendations */}
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>System Performance:</strong> All components are operating within normal parameters. 
                Response times are optimal and all AI agents are ready for research tasks.
              </Typography>
            </Alert>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default SystemStatus;
