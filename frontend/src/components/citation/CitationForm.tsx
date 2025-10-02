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
  Grid,
  IconButton,
  SelectChangeEvent
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import citationApi from '../../services/citationApi';
import CitationPreview from './CitationPreview';
import { Author, SourceType, CitationStyle, SourceMetadata, Citation } from '../../types/citation';

const CitationForm: React.FC = () => {
  const [sourceType, setSourceType] = useState<SourceType>('journal_article');
  const [style, setStyle] = useState<CitationStyle>('apa_7');
  const [citation, setCitation] = useState<Citation | null>(null);
  const [loading, setLoading] = useState(false);

  // Form fields
  const [title, setTitle] = useState('');
  const [authors, setAuthors] = useState<Author[]>([{ first_name: '', last_name: '', middle_name: '' }]);
  const [year, setYear] = useState('');
  const [publication, setPublication] = useState('');
  const [volume, setVolume] = useState('');
  const [issue, setIssue] = useState('');
  const [pages, setPages] = useState('');
  const [doi, setDoi] = useState('');
  const [url, setUrl] = useState('');
  const [publisher, setPublisher] = useState('');

  const addAuthor = () => {
    setAuthors([...authors, { first_name: '', last_name: '', middle_name: '' }]);
  };

  const removeAuthor = (index: number) => {
    setAuthors(authors.filter((_, i) => i !== index));
  };

  const updateAuthor = (index: number, field: keyof Author, value: string) => {
    const newAuthors = [...authors];
    newAuthors[index] = { ...newAuthors[index], [field]: value };
    setAuthors(newAuthors);
  };

  const handleGenerate = async () => {
    setLoading(true);

    const metadata: SourceMetadata = {
      source_type: sourceType,
      title,
      authors: authors.filter(a => a.first_name && a.last_name),
      year: year ? parseInt(year) : null,
      publication: publication || null,
      volume: volume || null,
      issue: issue || null,
      pages: pages || null,
      doi: doi || null,
      url: url || null,
      publisher: publisher || null
    };

    try {
      const result = await citationApi.generateCitation(metadata, style);
      setCitation(result);
    } catch (error) {
      console.error('Generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSourceTypeChange = (event: SelectChangeEvent<SourceType>) => {
    setSourceType(event.target.value as SourceType);
  };

  const handleStyleChange = (event: SelectChangeEvent<CitationStyle>) => {
    setStyle(event.target.value as CitationStyle);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 3 }}>Manual Citation Entry</Typography>

        <Grid container spacing={2}>
          {/* Source Type */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Source Type</InputLabel>
              <Select<SourceType> value={sourceType} onChange={handleSourceTypeChange} label="Source Type">
                <MenuItem value="journal_article">Journal Article</MenuItem>
                <MenuItem value="book">Book</MenuItem>
                <MenuItem value="website">Website</MenuItem>
                <MenuItem value="conference_paper">Conference Paper</MenuItem>
                <MenuItem value="thesis">Thesis</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Citation Style */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Citation Style</InputLabel>
              <Select<CitationStyle> value={style} onChange={handleStyleChange} label="Citation Style">
                <MenuItem value="apa_7">APA 7th</MenuItem>
                <MenuItem value="mla_9">MLA 9th</MenuItem>
                <MenuItem value="chicago_17">Chicago 17th</MenuItem>
                <MenuItem value="ieee">IEEE</MenuItem>
                <MenuItem value="harvard">Harvard</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Title */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </Grid>

          {/* Authors */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Authors</Typography>
            {authors.map((author, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  label="First Name"
                  value={author.first_name}
                  onChange={(e) => updateAuthor(index, 'first_name', e.target.value)}
                  size="small"
                />
                <TextField
                  label="Middle"
                  value={author.middle_name || ''}
                  onChange={(e) => updateAuthor(index, 'middle_name', e.target.value)}
                  size="small"
                  sx={{ width: 100 }}
                />
                <TextField
                  label="Last Name"
                  value={author.last_name}
                  onChange={(e) => updateAuthor(index, 'last_name', e.target.value)}
                  size="small"
                />
                <IconButton size="small" onClick={() => removeAuthor(index)} disabled={authors.length === 1}>
                  <DeleteIcon />
                </IconButton>
              </Box>
            ))}
            <Button size="small" startIcon={<AddIcon />} onClick={addAuthor}>
              Add Author
            </Button>
          </Grid>

          {/* Year */}
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Year"
              type="number"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            />
          </Grid>

          {/* Publication/Journal */}
          <Grid item xs={12} sm={8}>
            <TextField
              fullWidth
              label={sourceType === 'book' ? 'Publisher' : 'Publication/Journal'}
              value={sourceType === 'book' ? publisher : publication}
              onChange={(e) => sourceType === 'book' ? setPublisher(e.target.value) : setPublication(e.target.value)}
            />
          </Grid>

          {/* Volume, Issue, Pages */}
          {sourceType === 'journal_article' && (
            <>
              <Grid item xs={4}>
                <TextField fullWidth label="Volume" value={volume} onChange={(e) => setVolume(e.target.value)} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Issue" value={issue} onChange={(e) => setIssue(e.target.value)} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Pages" value={pages} onChange={(e) => setPages(e.target.value)} placeholder="123-145" />
              </Grid>
            </>
          )}

          {/* DOI */}
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="DOI" value={doi} onChange={(e) => setDoi(e.target.value)} placeholder="10.1000/xyz123" />
          </Grid>

          {/* URL */}
          <Grid item xs={12} sm={6}>
            <TextField fullWidth label="URL" value={url} onChange={(e) => setUrl(e.target.value)} />
          </Grid>

          {/* Generate Button */}
          <Grid item xs={12}>
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={handleGenerate}
              disabled={loading || !title || authors.every(a => !a.last_name)}
            >
              {loading ? 'Generating...' : 'Generate Citation'}
            </Button>
          </Grid>
        </Grid>

        {/* Preview */}
        {citation && (
          <Box sx={{ mt: 3 }}>
            <CitationPreview citation={citation} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CitationForm;
