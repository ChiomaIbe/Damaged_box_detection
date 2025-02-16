from fastapi import APIRouter, WebSocket, HTTPException
from models.detector import ObjectDetector
import os
import base64
from typing import Optional
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize detector with model
try:
    # Look for model in the project root directory
    model_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "best.pt"))
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    detector = ObjectDetector(model_path)
    logger.info(f"Model loaded successfully from {model_path}")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Failed to initialize model: {str(e)}")

@router.websocket("/ws/detect")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("New WebSocket connection established")
    
    try:
        while True:
            try:
                # Receive frame as base64 string
                frame_data = await websocket.receive_text()
                
                if not frame_data:
                    logger.warning("Received empty frame data")
                    await websocket.send_json({
                        "error": "Empty frame data received"
                    })
                    continue
                
                try:
                    # Split the base64 string and decode
                    frame_parts = frame_data.split(',')
                    if len(frame_parts) != 2:
                        raise ValueError("Invalid frame data format")
                    
                    frame_bytes = base64.b64decode(frame_parts[1])
                    
                    # Preprocess frame
                    frame = detector.preprocess_frame(frame_bytes)
                    if frame is None:
                        raise ValueError("Failed to decode frame")
                    
                    # Process frame and get detections
                    counts, detections = detector.process_frame(frame)
                    
                    # Send results back to client
                    await websocket.send_json({
                        "status": "success",
                        "counts": counts,
                        "detections": detections
                    })
                    
                except ValueError as ve:
                    logger.error(f"Frame processing error: {str(ve)}")
                    await websocket.send_json({
                        "status": "error",
                        "error": f"Frame processing error: {str(ve)}"
                    })
                except Exception as e:
                    logger.error(f"Unexpected error during frame processing: {str(e)}")
                    await websocket.send_json({
                        "status": "error",
                        "error": "Internal processing error"
                    })
                    
            except Exception as e:
                logger.error(f"WebSocket communication error: {str(e)}")
                await websocket.send_json({
                    "status": "error",
                    "error": "Communication error"
                })
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        logger.info("WebSocket connection closed")
        await websocket.close()