import React, { useState } from 'react';
import { Container, Typography, CssBaseline, ThemeProvider, createTheme, useMediaQuery } from '@mui/material';
import WebcamStream from './components/WebcamStream';
import Counter from './components/Counter';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2e7d32',
      dark: '#1b5e20',
    },
    error: {
      main: '#d32f2f',
      dark: '#c62828',
    },
  },
});

function App() {
  const isMobile = useMediaQuery('(max-width:600px)');
  const [detectionData, setDetectionData] = useState({ counts: { box: 0, damaged_box: 0 }, detections: [] });

  const handleDetectionsUpdate = (data) => {
    setDetectionData(data);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container 
        maxWidth="md" 
        sx={{ 
          py: { xs: 2, sm: 4 },
          px: { xs: 1, sm: 2, md: 3 }
        }}
      >
        <Typography 
          variant={isMobile ? "h4" : "h3"}
          component="h1" 
          gutterBottom 
          align="center"
          sx={{ mb: { xs: 2, sm: 4 } }}
        >
          Box Detection System
        </Typography>
        <Typography 
          variant="h6" 
          component="h2" 
          gutterBottom 
          align="center"
          sx={{ mb: { xs: 2, sm: 4 }, color: 'text.secondary' }}
        >
          By Precious Ibeakanma
        </Typography>

        <WebcamStream onDetectionsUpdate={handleDetectionsUpdate} />
        <Counter counts={detectionData.counts} />
      </Container>
    </ThemeProvider>
  );
}

export default App;
