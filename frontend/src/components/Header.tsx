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
    <AppBar position="sticky" elevation={0} sx={{ backgroundColor: 'rgba(19, 47, 76, 0.8)', backdropFilter: 'blur(20px)' }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          {/* Logo & Title */}
          <Box display="flex" alignItems="center" sx={{ flexGrow: 0 }}>
            <Psychology sx={{ mr: 1, fontSize: '2rem', color: 'primary.main' }} />
            <Typography variant="h6" component="div" sx={{ fontWeight: 700, letterSpacing: '0.5px' }}>
              AI Research Assistant
            </Typography>
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
