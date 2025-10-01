import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
  Divider,
  Alert,
} from '@mui/material';
import {
  Analytics,
  Chat,
  FindInPage,
  Lightbulb,
  TrendingUp,
  AutoAwesome,
} from '@mui/icons-material';
import DocumentUpload from '../components/DocumentUpload';

const DocumentAnalysis: React.FC = () => {
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [totalDocuments, setTotalDocuments] = useState(0);
  const [totalChunks, setTotalChunks] = useState(0);

  const handleDocumentUploaded = (document: any) => {
    setSelectedDocument(document);
    setTotalDocuments(prev => prev + 1);
    setTotalChunks(prev => prev + document.chunks_count);
  };

  const features = [
    {
      icon: <FindInPage color="primary" />,
      title: 'Smart Document Processing',
      description: 'Extract text, metadata, and create intelligent chunks for analysis',
      status: '✅ Available'
    },
    {
      icon: <Chat color="primary" />,
      title: 'RAG Chatbot',
      description: 'Ask questions about your documents with context-aware AI',
      status: '🚧 Coming Soon'
    },
    {
      icon: <Analytics color="primary" />,
      title: 'Content Analysis',
      description: 'Key insights, summaries, and important concepts extraction',
      status: '🚧 Coming Soon'
    },
    {
      icon: <Lightbulb color="primary" />,
      title: 'Research Insights',
      description: 'AI-powered research gap analysis and recommendations',
      status: '🚧 Coming Soon'
    },
    {
      icon: <TrendingUp color="primary" />,
      title: 'Cross-Document Analysis',
      description: 'Compare and analyze multiple documents together',
      status: '🔮 Planned'
    },
    {
      icon: <AutoAwesome color="primary" />,
      title: 'Integration with ArXiv',
      description: 'Combine your documents with global research discovery',
      status: '🔮 Planned'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={4}>
        {/* Left Column - Upload & Management */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              📤 Upload Documents
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Upload your research papers, notes, or documents for AI-powered analysis
            </Typography>
            
            <DocumentUpload onDocumentUploaded={handleDocumentUploaded} />
          </Paper>

          {/* Features Grid */}
          <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
            🚀 Platform Capabilities
          </Typography>
          
          <Grid container spacing={2}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      {feature.icon}
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {feature.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {feature.description}
                    </Typography>
                    <Chip 
                      label={feature.status} 
                      size="small" 
                      color={feature.status.includes('Available') ? 'success' : 'default'}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Right Column - Info & Preview */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              🤖 RAG Chat Preview
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Soon you'll be able to chat with your documents!
            </Typography>
            
            <Box sx={{ 
              p: 2, 
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              backgroundColor: 'background.paper',
              mb: 2
            }}>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                <strong>You:</strong> What are the main findings in this paper?<br/><br/>
                <strong>AI:</strong> Based on the uploaded document, the main findings are...<br/><br/>
                <strong>You:</strong> Can you summarize the methodology?<br/><br/>
                <strong>AI:</strong> The methodology section describes...
              </Typography>
            </Box>
            
            <Button 
              variant="outlined" 
              fullWidth 
              disabled
              startIcon={<Chat />}
            >
              Coming Soon: Start Chat
            </Button>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              📊 Processing Stats
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Documents Processed
              </Typography>
              <Typography variant="h4" color="primary">
                {totalDocuments}
              </Typography>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Total Chunks Created
              </Typography>
              <Typography variant="h4" color="secondary">
                {totalChunks}
              </Typography>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Box>
              <Typography variant="body2" color="text.secondary">
                Supported Formats
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Chip label="PDF" size="small" sx={{ mr: 1, mb: 1 }} />
                <Chip label="DOCX" size="small" sx={{ mr: 1, mb: 1 }} />
                <Chip label="TXT" size="small" sx={{ mr: 1, mb: 1 }} />
                <Chip label="MD" size="small" sx={{ mr: 1, mb: 1 }} />
              </Box>
            </Box>
          </Paper>

          {selectedDocument && (
            <Alert severity="success" sx={{ mt: 2 }}>
              🎉 Document "{selectedDocument.original_filename}" processed successfully! 
              Created {selectedDocument.chunks_count} chunks. Chat feature coming soon.
            </Alert>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default DocumentAnalysis;
