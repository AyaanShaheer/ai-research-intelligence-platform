import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Paper
} from '@mui/material';
import FormatQuoteIcon from '@mui/icons-material/FormatQuote';
import QuickCitation from '../components/citation/QuickCitation';
import CitationForm from '../components/citation/CitationForm';

const CitationGenerator: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <FormatQuoteIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        <Typography variant="h3" component="h1" gutterBottom>
          AI Citation Generator
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate accurate citations in APA, MLA, Chicago, IEEE, and more
        </Typography>
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} centered>
          <Tab label="Quick AI Citation" />
          <Tab label="Manual Entry" />
          <Tab label="From DOI/URL" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {activeTab === 0 && <QuickCitation />}
      {activeTab === 1 && <CitationForm />}
      {activeTab === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography>DOI/URL import coming soon...</Typography>
        </Paper>
      )}
    </Container>
  );
};

export default CitationGenerator;
