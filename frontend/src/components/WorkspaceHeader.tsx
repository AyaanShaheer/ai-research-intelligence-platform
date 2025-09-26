import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
  Avatar,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Psychology,
  Business,
  AccountCircle,
  Settings,
  Analytics,
} from '@mui/icons-material';

interface WorkspaceHeaderProps {
  workspaceName: string;
  userEmail: string;
  planType: string;
  usagePercentage: number;
}

const WorkspaceHeader: React.FC<WorkspaceHeaderProps> = ({
  workspaceName,
  userEmail,
  planType,
  usagePercentage
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const getPlanColor = () => {
    switch (planType) {
      case 'enterprise': return 'success';
      case 'pro': return 'warning';
      default: return 'default';
    }
  };

  return (
    <AppBar position="sticky" elevation={0} sx={{ backgroundColor: 'rgba(19, 47, 76, 0.95)', backdropFilter: 'blur(20px)' }}>
      <Toolbar>
        {/* Logo & Workspace */}
        <Box display="flex" alignItems="center" sx={{ flexGrow: 1 }}>
          <Psychology sx={{ mr: 1, fontSize: '2rem', color: 'primary.main' }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              AI Research Intelligence
            </Typography>
            <Typography variant="caption" color="text.secondary">
              <Business sx={{ fontSize: '0.8rem', mr: 0.5 }} />
              {workspaceName}
            </Typography>
          </Box>
        </Box>

        {/* Usage & Plan Info */}
        <Box display="flex" alignItems="center" gap={2} mr={2}>
          <Chip
            label={`${planType.toUpperCase()} Plan`}
            size="small"
            color={getPlanColor() as any}
            sx={{ fontWeight: 600 }}
          />
          <Box>
            <Typography variant="caption" color="text.secondary">
              Usage: {usagePercentage}%
            </Typography>
          </Box>
        </Box>

        {/* User Menu */}
        <Button
          color="inherit"
          onClick={(e) => setAnchorEl(e.currentTarget)}
          startIcon={<AccountCircle />}
        >
          {userEmail}
        </Button>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          <MenuItem onClick={() => setAnchorEl(null)}>
            <Analytics sx={{ mr: 1 }} /> Workspace Analytics
          </MenuItem>
          <MenuItem onClick={() => setAnchorEl(null)}>
            <Settings sx={{ mr: 1 }} /> Settings
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default WorkspaceHeader;
