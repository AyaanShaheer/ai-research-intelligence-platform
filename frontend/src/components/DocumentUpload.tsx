import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  PictureAsPdf,
  Delete,
  Visibility,
  Chat,
  Send,
} from '@mui/icons-material';

interface UploadedDocument {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  status: string;
  chunks_count: number;
  processing_time: number;
  metadata: {
    word_count: number;
    pages?: number;
  };
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: any[];
}

interface DocumentUploadProps {
  onDocumentUploaded?: (document: UploadedDocument) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onDocumentUploaded }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  
  // Chat states
  const [chatOpen, setChatOpen] = useState(false);
  const [currentDoc, setCurrentDoc] = useState<UploadedDocument | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [messageInput, setMessageInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const handleFile = async (file: File) => {
    const allowedTypes = ['.pdf', '.docx', '.txt', '.md'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
      setError(`Unsupported file type. Please upload: ${allowedTypes.join(', ')}`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size too large. Maximum size is 10MB.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', `Uploaded via CiteOn AI interface - ${new Date().toISOString()}`);

      const response = await fetch('http://localhost:8000/documents/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok && result.success) {
        const newDoc = result.document;
        setUploadedDocs(prev => [...prev, newDoc]);
        setSuccess(`✅ ${file.name} processed successfully! Created ${newDoc.chunks_count} chunks in ${newDoc.processing_time?.toFixed(2)}s.`);
        onDocumentUploaded?.(newDoc);
      } else {
        setError(result.detail || result.message || 'Upload failed');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(`Upload error: ${err instanceof Error ? err.message : 'Network error'}`);
    } finally {
      setUploading(false);
    }
  };

  // Chat functions with better error handling
  const startChat = async (document: UploadedDocument) => {
    try {
      setChatLoading(true);
      console.log('Starting chat for document:', document.id);
      
      const response = await fetch('http://localhost:8000/chat/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_ids: [document.id],
          session_name: `Chat with ${document.original_filename}`
        })
      });

      const result = await response.json();
      console.log('Chat start response:', result);
      
      if (response.ok) {
        setSessionId(result.session_id);
        setCurrentDoc(document);
        setMessages([{
          role: 'assistant',
          content: `Hello! I'm ready to answer questions about "${document.original_filename}". What would you like to know?`,
          timestamp: new Date().toISOString()
        }]);
        setChatOpen(true);
      } else {
        setError(`Failed to start chat: ${result.detail || 'Unknown error'}`);
        console.error('Chat start failed:', result);
      }
    } catch (err) {
      console.error('Chat start error:', err);
      setError(`Chat error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setChatLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!messageInput.trim() || !sessionId) return;

    const originalMessage = messageInput;
    const userMessage: ChatMessage = {
      role: 'user',
      content: originalMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setMessageInput('');
    setChatLoading(true);

    try {
      console.log('Sending message:', originalMessage);
      console.log('Session ID:', sessionId);
      
      const response = await fetch(`http://localhost:8000/chat/${sessionId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: originalMessage })
      });

      console.log('Message response status:', response.status);
      const result = await response.json();
      console.log('Message response data:', result);

      if (response.ok) {
        const aiMessage: ChatMessage = {
          role: 'assistant',
          content: result.ai_response || result.content || 'I received your message but had trouble generating a response.',
          timestamp: new Date().toISOString(),
          sources: result.sources || []
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `❌ Error: ${result.detail || 'Unknown error occurred'}`,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (err) {
      console.error('Message send error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `🔌 Connection error: ${err instanceof Error ? err.message : 'Unknown error'}. Is the backend running?`,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
    e.target.value = '';
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf': return <PictureAsPdf color="error" />;
      case 'docx': return <Description color="info" />;
      default: return <Description color="action" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <Box>
      {/* Upload Area */}
      <Paper
        sx={{
          p: 4,
          textAlign: 'center',
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.500',
          backgroundColor: dragActive ? 'action.hover' : 'transparent',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="fileInput"
          style={{ display: 'none' }}
          onChange={handleFileInput}
          accept=".pdf,.docx,.txt,.md"
        />
        
        <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {dragActive ? 'Drop your document here' : 'Upload Research Document'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Drag and drop or click to select • PDF, DOCX, TXT, MD • Max 10MB
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap', mb: 2 }}>
          <Chip label="📄 PDF" size="small" />
          <Chip label="📝 DOCX" size="small" />
          <Chip label="📋 TXT" size="small" />
          <Chip label="📑 Markdown" size="small" />
        </Box>
        <Button
          variant="contained"
          onClick={() => document.getElementById('fileInput')?.click()}
          disabled={uploading}
        >
          {uploading ? 'Processing...' : 'Choose Document'}
        </Button>
      </Paper>

      {/* Progress, Success, Error */}
      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
            Processing document and creating intelligent chunks...
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mt: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Documents List */}
      {uploadedDocs.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            📚 Processed Documents ({uploadedDocs.length})
          </Typography>
          
          <Paper sx={{ mt: 2 }}>
            <List>
              {uploadedDocs.map((doc) => (
                <ListItem key={doc.id} divider>
                  <Box sx={{ mr: 2 }}>
                    {getFileIcon(doc.file_type)}
                  </Box>
                  
                  <ListItemText
                    primary={doc.original_filename}
                    secondary={
                      <Box sx={{ mt: 0.5 }}>
                        <Typography variant="caption" display="block">
                          📊 {doc.metadata.word_count} words • 
                          🧩 {doc.chunks_count} chunks • 
                          📁 {formatFileSize(doc.file_size)} • 
                          ⚡ {doc.processing_time?.toFixed(2)}s
                        </Typography>
                        <Box sx={{ mt: 0.5 }}>
                          <Chip 
                            label={doc.status} 
                            size="small" 
                            color={doc.status === 'completed' ? 'success' : 'warning'}
                          />
                        </Box>
                      </Box>
                    }
                  />
                  
                  <ListItemSecondaryAction>
                    <IconButton edge="end" sx={{ mr: 1 }} title="Preview Document">
                      <Visibility />
                    </IconButton>
                    <IconButton 
                      edge="end" 
                      sx={{ mr: 1 }}
                      color="primary"
                      title="Start Chat with Document"
                      onClick={() => startChat(doc)}
                      disabled={chatLoading}
                    >
                      <Chat />
                    </IconButton>
                    <IconButton 
                      edge="end" 
                      color="error"
                      title="Delete Document"
                      onClick={() => setUploadedDocs(prev => prev.filter(d => d.id !== doc.id))}
                    >
                      <Delete />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Box>
      )}

      {/* FIXED Chat Dialog with Proper Colors */}
      <Dialog 
        open={chatOpen} 
        onClose={() => setChatOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { 
            height: '80vh',
            backgroundColor: '#132F4C'
          }
        }}
      >
        <DialogTitle sx={{ 
          backgroundColor: '#0A1929', 
          color: '#FFFFFF',
          borderBottom: '1px solid #2196F3'
        }}>
          🤖 Chat with {currentDoc?.original_filename}
        </DialogTitle>
        
        <DialogContent sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: '100%',
          backgroundColor: '#132F4C',
          p: 2
        }}>
          <Box sx={{ 
            flexGrow: 1, 
            overflowY: 'auto', 
            border: '1px solid #2196F3',
            borderRadius: 2,
            p: 2,
            mb: 2,
            backgroundColor: '#0A1929',
            minHeight: '400px'
          }}>
            {messages.map((msg, index) => (
              <Box key={index} sx={{ 
                mb: 2, 
                p: 2, 
                borderRadius: 2,
                backgroundColor: msg.role === 'user' ? '#2196F3' : '#4CAF50',
                color: '#FFFFFF', // Always white text
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
                ml: msg.role === 'user' ? 'auto' : 0,
                mr: msg.role === 'user' ? 0 : 'auto',
                display: 'flex',
                flexDirection: 'column'
              }}>
                <Typography variant="body1" sx={{ 
                  color: '#FFFFFF', 
                  fontWeight: 'bold', 
                  mb: 0.5,
                  fontSize: '0.9rem'
                }}>
                  {msg.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                </Typography>
                <Typography variant="body2" sx={{ 
                  color: '#FFFFFF', 
                  lineHeight: 1.5,
                  fontSize: '0.9rem'
                }}>
                  {msg.content}
                </Typography>
                {msg.sources && msg.sources.length > 0 && (
                  <Typography variant="caption" display="block" sx={{ 
                    mt: 1, 
                    color: '#E3F2FD',
                    fontStyle: 'italic'
                  }}>
                    📚 Sources: {msg.sources.length} references found
                  </Typography>
                )}
              </Box>
            ))}
            
            {chatLoading && (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <LinearProgress sx={{ mb: 2, backgroundColor: '#2196F3' }} />
                <Typography variant="body2" sx={{ color: '#FFFFFF' }}>
                  🤔 AI is analyzing your document...
                </Typography>
              </Box>
            )}
          </Box>

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="Ask about this document..."
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
              disabled={chatLoading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#0A1929',
                  color: '#FFFFFF',
                  '& fieldset': {
                    borderColor: '#2196F3',
                  },
                  '&:hover fieldset': {
                    borderColor: '#64B5F6',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#2196F3',
                  },
                },
                '& .MuiInputBase-input::placeholder': {
                  color: '#B2BAC2',
                  opacity: 1,
                },
              }}
            />
            <Button
              variant="contained"
              onClick={sendMessage}
              disabled={chatLoading || !messageInput.trim()}
              startIcon={<Send />}
              sx={{
                minWidth: '100px',
                height: '56px',
                backgroundColor: '#2196F3',
                '&:hover': {
                  backgroundColor: '#1976D2',
                }
              }}
            >
              Send
            </Button>
          </Box>
        </DialogContent>

        <DialogActions sx={{ 
          backgroundColor: '#0A1929',
          borderTop: '1px solid #2196F3',
          p: 2
        }}>
          <Button 
            onClick={() => setChatOpen(false)}
            sx={{ color: '#2196F3' }}
          >
            Close Chat
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentUpload;
