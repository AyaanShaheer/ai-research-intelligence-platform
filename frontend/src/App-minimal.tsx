import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { 
  CssBaseline, 
  Container, 
  Typography, 
  Box, 
  Button,
  Paper,
  Card,
  CardContent 
} from '@mui/material';
import { Psychology, Search, Assessment } from '@mui/icons-material';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#2196F3' },
    secondary: { main: '#4CAF50' },
    background: {
      default: '#0A1929',
      paper: '#132F4C',
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4 }}>
        <Container maxWidth="xl">
          {/* Header */}
          <Box display="flex" alignItems="center" mb={4}>
            <Psychology sx={{ fontSize: '3rem', mr: 2, color: 'primary.main' }} />
            <Box>
              <Typography variant="h3" component="h1" gutterBottom>
                🚀 AI Research Assistant
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Multi-Agent Research Pipeline - Now with Material-UI!
              </Typography>
            </Box>
          </Box>

          {/* Status Cards */}
          <Box display="flex" gap={3} mb={4}>
            <Card sx={{ flex: 1 }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Assessment sx={{ fontSize: '2rem', color: 'primary.main', mb: 1 }} />
                <Typography variant="h6">Dashboard</Typography>
                <Typography variant="body2" color="text.secondary">
                  System overview
                </Typography>
              </CardContent>
            </Card>
            
            <Card sx={{ flex: 1 }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Search sx={{ fontSize: '2rem', color: 'secondary.main', mb: 1 }} />
                <Typography variant="h6">Research</Typography>
                <Typography variant="body2" color="text.secondary">
                  AI-powered analysis
                </Typography>
              </CardContent>
            </Card>
          </Box>

          {/* Action Area */}
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              🎯 Ready for Research
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Your multi-agent research assistant is ready to analyze academic papers
            </Typography>
            <Button 
              variant="contained" 
              size="large" 
              startIcon={<Search />}
              sx={{ 
                px: 4, 
                py: 1.5,
                background: 'linear-gradient(45deg, #2196F3 30%, #4CAF50 90%)'
              }}
            >
              Start Research
            </Button>
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default App;
