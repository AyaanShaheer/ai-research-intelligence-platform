import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
  Container,
} from '@mui/material';
import {
  Psychology,
  Search,
  Assessment,
  Settings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { label: 'Dashboard', path: '/', icon: <Assessment /> },
    { label: 'Research', path: '/research', icon: <Search /> },
    { label: 'System', path: '/system', icon: <Settings /> },
  ];

  return (
    <AppBar position="sticky" elevation={0} sx={{ backgroundColor: 'rgba(19, 47, 76, 0.95)', backdropFilter: 'blur(20px)' }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          {/* Logo & Brand */}
          <Box display="flex" alignItems="center" sx={{ flexGrow: 0, mr: 4 }}>
            {/* CITEON Logo */}
            <Box 
              component="img" 
              src="/images/citeon-logo.png" 
              alt="CITEON Logo"
              sx={{ 
                height: '40px', 
                width: '40px', 
                mr: 2,
                cursor: 'pointer',
                '&:hover': {
                  transform: 'scale(1.05)',
                  transition: 'transform 0.2s ease'
                }
              }}
              onClick={() => navigate('/')}
            />
            <Box>
              <Typography 
                variant="h6" 
                component="div" 
                sx={{ 
                  fontWeight: 700, 
                  letterSpacing: '0.5px',
                  background: 'linear-gradient(45deg, #FFFFFF 30%, #64B5F6 90%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  color: 'transparent',
                  fontSize: '1.3rem'
                }}
              >
                CITEON
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255,255,255,0.7)',
                  fontSize: '0.7rem',
                  fontWeight: 500,
                  display: 'block',
                  lineHeight: 0.8,
                  mt: -0.5
                }}
              >
                CITE ASK TRUST
              </Typography>
            </Box>
            <Chip
              label="Multi-Agent"
              size="small"
              color="secondary"
              sx={{ ml: 2, fontSize: '0.7rem', fontWeight: 600 }}
            />
          </Box>

          {/* Navigation */}
          <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                onClick={() => navigate(item.path)}
                startIcon={item.icon}
                sx={{
                  mx: 1,
                  color: location.pathname === item.path ? 'primary.main' : 'text.secondary',
                  fontWeight: location.pathname === item.path ? 600 : 400,
                  borderRadius: 2,
                  px: 3,
                  '&:hover': {
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    color: 'primary.light',
                  },
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>

          {/* Status Indicator */}
          <Box>
            <Chip
              label="🟢 Online"
              size="small"
              sx={{ 
                backgroundColor: 'rgba(76, 175, 80, 0.2)', 
                color: 'secondary.main',
                fontWeight: 600,
              }}
            />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
