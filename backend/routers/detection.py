from fastapi import APIRouter, WebSocket, HTTPException, WebSocketDisconnect
from models.detector import ObjectDetector
import os
import base64
from typing import Optional, Dict
import logging
import asyncio
import json

router = APIRouter()

# Store active connections
active_connections: Dict[WebSocket, bool] = {}

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

async def heartbeat(websocket: WebSocket):
    """Send periodic heartbeat to keep connection alive"""
    try:
        while active_connections.get(websocket, False):
            await websocket.send_json({"type": "ping"})
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
    except Exception as e:
        logger.error(f"Heartbeat error: {str(e)}")
        active_connections[websocket] = False

@router.websocket("/ws/detect")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections[websocket] = True
    logger.info("New WebSocket connection established")
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat(websocket))
    
    try:
        while active_connections.get(websocket, False):
            try:
                # Receive data
                data = await websocket.receive()
                
                # Handle heartbeat response
                if data.get("type") == "text" and data.get("text") == "pong":
                    continue
                
                # Get frame data
                frame_data = data.get("text", "")
                
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
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        # Clean up
        active_connections[websocket] = False
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        
        if websocket in active_connections:
            del active_connections[websocket]
            
        logger.info("WebSocket connection closed")
        try:
            await websocket.close()
        except RuntimeError:
            # Connection might already be closed
            pass
