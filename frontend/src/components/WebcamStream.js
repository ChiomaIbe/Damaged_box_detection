import React, { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import { Box, Paper, Button, Stack, Switch, FormControlLabel, Input, Select, MenuItem, FormControl, InputLabel, useMediaQuery, useTheme } from '@mui/material';

const WebcamStream = ({ onDetectionsUpdate }) => {
    const webcamRef = useRef(null);
    const canvasRef = useRef(null);
    const wsRef = useRef(null);
    const [isConnected, setIsConnected] = useState(false);
    const [isRunning, setIsRunning] = useState(false);
    const [useWebcam, setUseWebcam] = useState(true);
    const [selectedFile, setSelectedFile] = useState(null);
    const [devices, setDevices] = useState([]);
    const [selectedDevice, setSelectedDevice] = useState(null);
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    
    const getVideoConstraints = () => {
        const baseConstraints = {
            deviceId: selectedDevice ? { exact: selectedDevice } : undefined
        };

        if (isMobile) {
            return {
                ...baseConstraints,
                width: window.innerWidth < 350 ? 320 : 480,
                height: window.innerWidth < 350 ? 240 : 360,
                facingMode: { ideal: 'environment' } // Prefer back camera on mobile
            };
        }

        return {
            ...baseConstraints,
            width: 640,
            height: 480
        };
    };

    const videoConstraints = getVideoConstraints();

    useEffect(() => {
        // Get list of video input devices
        navigator.mediaDevices.enumerateDevices()
            .then(devices => {
                const videoDevices = devices.filter(device => device.kind === 'videoinput');
                setDevices(videoDevices);
                if (videoDevices.length > 0) {
                    setSelectedDevice(videoDevices[0].deviceId);
                }
            })
            .catch(err => {
                console.error("Error getting devices:", err);
            });
    }, []);

    const handleDeviceChange = (event) => {
        setSelectedDevice(event.target.value);
    };

    useEffect(() => {
        // Setup WebSocket connection
        const connectWebSocket = () => {
            const ws = new WebSocket('wss://damaged-box-detection-1.onrender.com/ws/detect');
            
            ws.onopen = () => {
                console.log('WebSocket Connected');
                setIsConnected(true);
            };

            ws.onclose = () => {
                console.log('WebSocket Disconnected');
                setIsConnected(false);
                // Attempt to reconnect after 2 seconds
                setTimeout(connectWebSocket, 2000);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.error) {
                    console.error('Detection error:', data.error);
                    return;
                }
                
                // Update detections and counts
                onDetectionsUpdate(data);
                
                // Draw detections on canvas
                drawDetections(data.detections);
            };

            wsRef.current = ws;
        };

        connectWebSocket();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [onDetectionsUpdate]);

    const drawDetections = (detections) => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        
        // Clear previous drawings
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        detections.forEach(detection => {
            const [x1, y1, x2, y2] = detection.bbox;
            const width = x2 - x1;
            const height = y2 - y1;
            
            // Set style based on class
            ctx.strokeStyle = detection.class === 'damaged_box' ? '#ff0000' : '#00ff00';
            ctx.lineWidth = 2;
            
            // Draw bounding box
            ctx.strokeRect(x1, y1, width, height);
            
            // Draw label
            ctx.fillStyle = ctx.strokeStyle;
            ctx.font = '16px Arial';
            ctx.fillText(
                `${detection.class} ${Math.round(detection.confidence * 100)}%`,
                x1,
                y1 > 20 ? y1 - 5 : y1 + 20
            );
        });
    };

    const captureFrame = () => {
        if (!isConnected || !wsRef.current) return;

        if (useWebcam) {
            if (webcamRef.current) {
                const imageSrc = webcamRef.current.getScreenshot();
                if (imageSrc) {
                    wsRef.current.send(imageSrc);
                }
            }
        } else if (selectedFile) {
            // Send the selected file
            const reader = new FileReader();
            reader.onloadend = () => {
                wsRef.current.send(reader.result.split(',')[1]); // Send base64 data
            };
            reader.readAsDataURL(selectedFile);
        }
    };

    const handleFileChange = (event) => {
        if (event.target.files && event.target.files[0]) {
            setSelectedFile(event.target.files[0]);
        }
    };

    const handleToggleWebcam = () => {
        setUseWebcam(!useWebcam);
        setIsRunning(false); // Stop detection when switching modes
        setSelectedFile(null); // Clear selected file when switching to webcam
    };

    useEffect(() => {
        let interval;
        if (isRunning && isConnected) {
            interval = setInterval(captureFrame, 100); // 10 FPS
        }
        return () => clearInterval(interval);
    }, [isConnected, isRunning]);

    const handleStartStop = () => {
        setIsRunning(!isRunning);
    };

    return (
        <Stack spacing={2} alignItems="center">
            <FormControl fullWidth sx={{ maxWidth: { xs: '100%', sm: 400 } }}>
                <InputLabel>Camera Device</InputLabel>
                <Select
                    value={selectedDevice || ''}
                    onChange={handleDeviceChange}
                    label="Camera Device"
                >
                    {devices.map(device => (
                        <MenuItem key={device.deviceId} value={device.deviceId}>
                            {device.label || `Camera ${devices.indexOf(device) + 1}`}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            
            <Stack 
                direction={{ xs: 'column', sm: 'row' }} 
                spacing={2} 
                alignItems="center"
                sx={{ width: '100%' }}
            >
                <FormControlLabel
                    control={
                        <Switch
                            checked={useWebcam}
                            onChange={handleToggleWebcam}
                            color="primary"
                        />
                    }
                    label="Use Webcam"
                />
                {!useWebcam && (
                    <Input
                        type="file"
                        onChange={handleFileChange}
                        accept="image/*"
                        sx={{ 
                            display: !useWebcam ? 'block' : 'none',
                            width: '100%',
                            maxWidth: { xs: '100%', sm: 400 }
                        }}
                    />
                )}
            </Stack>

            <Button
                variant="contained"
                color={isRunning ? "error" : "primary"}
                onClick={handleStartStop}
                disabled={!useWebcam && !selectedFile}
                sx={{ 
                    mb: 2,
                    width: { xs: '100%', sm: 'auto' }
                }}
            >
                {isRunning ? "Stop Detection" : "Start Detection"}
            </Button>

            <Paper 
                elevation={3} 
                sx={{ 
                    position: 'relative',
                    width: 'fit-content',
                    maxWidth: '100%',
                    overflow: 'hidden'
                }}
            >
                <Box sx={{ position: 'relative' }}>
                    {useWebcam ? (
                        <Webcam
                            ref={webcamRef}
                            audio={false}
                            screenshotFormat="image/jpeg"
                            videoConstraints={videoConstraints}
                            style={{ 
                                display: 'block',
                                width: '100%',
                                height: 'auto'
                            }}
                        />
                    ) : (
                        selectedFile && (
                            <img
                                src={URL.createObjectURL(selectedFile)}
                                alt="Selected"
                                style={{
                                    width: '100%',
                                    height: 'auto',
                                    display: 'block',
                                    maxWidth: videoConstraints.width,
                                    maxHeight: videoConstraints.height
                                }}
                            />
                        )
                    )}
                    <canvas
                        ref={canvasRef}
                        width={videoConstraints.width}
                        height={videoConstraints.height}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            pointerEvents: 'none'
                        }}
                    />
                </Box>
            </Paper>
        </Stack>
    );
};

export default WebcamStream;
