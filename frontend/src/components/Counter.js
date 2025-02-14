import React from 'react';
import { Paper, Typography, Grid, Box, useMediaQuery, useTheme } from '@mui/material';

const Counter = ({ counts }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    return (
        <Paper 
            elevation={3} 
            sx={{ 
                padding: { xs: 1, sm: 2 },
                margin: { xs: '10px auto', sm: '20px auto' },
                maxWidth: 640,
                width: '100%'
            }}
        >
            <Grid container spacing={{ xs: 2, sm: 4 }} justifyContent="center">
                <Grid item xs={6}>
                    <Box 
                        sx={{ 
                            textAlign: 'center',
                            padding: { xs: 1, sm: 2 },
                            borderRadius: 1,
                            bgcolor: '#e8f5e9'
                        }}
                    >
                        <Typography 
                            variant={isMobile ? "subtitle1" : "h6"} 
                            color="primary"
                            sx={{ fontSize: { xs: '0.9rem', sm: '1.25rem' } }}
                        >
                            Normal Boxes
                        </Typography>
                        <Typography 
                            variant={isMobile ? "h4" : "h3"} 
                            color="primary.dark"
                            sx={{ fontSize: { xs: '2rem', sm: '3rem' } }}
                        >
                            {counts?.box || 0}
                        </Typography>
                    </Box>
                </Grid>
                <Grid item xs={6}>
                    <Box 
                        sx={{ 
                            textAlign: 'center',
                            padding: { xs: 1, sm: 2 },
                            borderRadius: 1,
                            bgcolor: '#ffebee'
                        }}
                    >
                        <Typography 
                            variant={isMobile ? "subtitle1" : "h6"} 
                            color="error"
                            sx={{ fontSize: { xs: '0.9rem', sm: '1.25rem' } }}
                        >
                            Damaged Boxes
                        </Typography>
                        <Typography 
                            variant={isMobile ? "h4" : "h3"} 
                            color="error.dark"
                            sx={{ fontSize: { xs: '2rem', sm: '3rem' } }}
                        >
                            {counts?.damaged_box || 0}
                        </Typography>
                    </Box>
                </Grid>
            </Grid>
        </Paper>
    );
};

export default Counter;
