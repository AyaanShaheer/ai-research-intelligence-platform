import React, { useState } from 'react';
import {
  Card,
  CardContent,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Typography,
  CircularProgress,
  Alert,
  SelectChangeEvent
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import citationApi from '../../services/citationApi';
import CitationPreview from './CitationPreview';
import { Citation, CitationStyle } from '../../types/citation';

const QuickCitation: React.FC = () => {
  const [text, setText] = useState('');
  const [style, setStyle] = useState<CitationStyle>('apa_7');
  const [loading, setLoading] = useState(false);
  const [citation, setCitation] = useState<Citation | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError('Please enter some text');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await citationApi.quickGenerate(text, style);
      setCitation(result);
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Failed to generate citation');
    } finally {
      setLoading(false);
    }
  };

  const handleStyleChange = (event: SelectChangeEvent<CitationStyle>) => {
    setStyle(event.target.value as CitationStyle);
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AutoAwesomeIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Quick AI Citation</Typography>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Describe your source in natural language and let AI extract the citation details
        </Typography>

        <TextField
          fullWidth
          multiline
          rows={3}
          placeholder='Example: "Cite Attention is All You Need by Vaswani from NIPS 2017"'
          value={text}
          onChange={(e) => setText(e.target.value)}
          sx={{ mb: 2 }}
        />

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Citation Style</InputLabel>
            <Select<CitationStyle> value={style} onChange={handleStyleChange} label="Citation Style">
              <MenuItem value="apa_7">APA 7th</MenuItem>
              <MenuItem value="mla_9">MLA 9th</MenuItem>
              <MenuItem value="chicago_17">Chicago 17th</MenuItem>
              <MenuItem value="ieee">IEEE</MenuItem>
              <MenuItem value="harvard">Harvard</MenuItem>
              <MenuItem value="vancouver">Vancouver</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={loading || !text.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
          >
            {loading ? 'Generating...' : 'Generate Citation'}
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {citation && <CitationPreview citation={citation} />}
      </CardContent>
    </Card>
  );
};

export default QuickCitation;
