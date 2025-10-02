import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Chip,
  Divider,
  Button,
  ButtonGroup
} from '@mui/material';
import CopyButton from '../common/CopyButton';
import DownloadIcon from '@mui/icons-material/Download';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import { Citation } from '../../types/citation';

interface CitationPreviewProps {
  citation: Citation;
  onSave?: (citation: Citation) => void;
}

const CitationPreview: React.FC<CitationPreviewProps> = ({ citation, onSave }) => {
  const handleDownload = (format: string) => {
    const blob = new Blob([citation.citation], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `citation.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Paper elevation={2} sx={{ p: 3, bgcolor: 'grey.50' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Generated Citation
        </Typography>
        <Chip label={citation.style.toUpperCase()} size="small" color="primary" />
      </Box>

      {/* Full Citation */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: 'white' }}>
        <Typography
          variant="body1"
          sx={{
            fontFamily: 'Georgia, serif',
            lineHeight: 1.8,
            textIndent: '-2em',
            paddingLeft: '2em'
          }}
        >
          {citation.citation}
        </Typography>
      </Paper>

      {/* In-text Citation */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5 }}>
          In-text citation:
        </Typography>
        <Paper variant="outlined" sx={{ p: 1, bgcolor: 'white', display: 'inline-block' }}>
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
            {citation.in_text_citation}
          </Typography>
        </Paper>
      </Box>

      {/* Warnings */}
      {citation.warnings && citation.warnings.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" color="warning.main" sx={{ mb: 0.5 }}>
            ⚠️ Warnings:
          </Typography>
          {citation.warnings.map((warning, idx) => (
            <Typography key={idx} variant="caption" display="block" color="text.secondary">
              • {warning}
            </Typography>
          ))}
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'space-between' }}>
        <ButtonGroup size="small" variant="outlined">
          <Button onClick={() => handleDownload('txt')} startIcon={<DownloadIcon />}>
            Text
          </Button>
          <Button onClick={() => handleDownload('bib')}>BibTeX</Button>
          <Button onClick={() => handleDownload('ris')}>RIS</Button>
        </ButtonGroup>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {onSave && (
            <Button
              size="small"
              variant="outlined"
              startIcon={<BookmarkIcon />}
              onClick={() => onSave(citation)}
            >
              Save to Library
            </Button>
          )}
          <CopyButton text={citation.citation} label="Copy citation" />
        </Box>
      </Box>
    </Paper>
  );
};

export default CitationPreview;
