import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container } from '@mui/material';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ResearchPage from './pages/ResearchPage';
import DocumentAnalysis from './pages/DocumentAnalysis';
import SystemStatus from './pages/SystemStatus';

// Create modern dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196F3',
      dark: '#1976D2',
      light: '#64B5F6',
    },
    secondary: {
      main: '#4CAF50',
      dark: '#388E3C',
      light: '#81C784',
    },
    background: {
      default: '#0A1929',
      paper: '#132F4C',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B2BAC2',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      color: '#FFFFFF',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      color: '#FFFFFF',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: '#FFFFFF',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    // Add global component styles
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div style={{ 
          minHeight: '100vh', 
          backgroundColor: theme.palette.background.default 
        }}>
          <Header />
          <Container maxWidth="xl" sx={{ py: 4 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/research" element={<ResearchPage />} />
              <Route path="/documents" element={<DocumentAnalysis />} />
              <Route path="/system" element={<SystemStatus />} />
              {/* Add a fallback route */}
              <Route path="*" element={<Dashboard />} />
            </Routes>
          </Container>
        </div>
      </Router>
    </ThemeProvider>
  );
};

export default App;
