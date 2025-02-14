import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self, model_path: str):
        try:
            # Load YOLO model directly from .pt file
            self.model = YOLO(model_path)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Failed to initialize model: {str(e)}")
        
        # Class names for our model
        self.classes = ["box", "damaged_box"]
        self.counts = {cls: 0 for cls in self.classes}
        
    def process_frame(self, frame: np.ndarray) -> Tuple[Dict[str, int], List[Dict]]:
        """
        Process a single frame and return detection results
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: frame is empty or None")
            
        # Reset counts for new frame
        self.counts = {cls: 0 for cls in self.classes}
        
        try:
            # Run detection with confidence threshold
            results = self.model(frame, conf=0.25)[0]
            
            # Process results
            detections = []
            boxes = results.boxes
            
            if len(boxes) > 0:
                for box in boxes:
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    if class_id < len(self.classes):
                        # Get box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        
                        # Get class name
                        class_name = self.classes[class_id]
                        
                        # Update counts
                        self.counts[class_name] += 1
                        
                        # Add detection to list
                        detections.append({
                            "bbox": [x1, y1, x2, y2],
                            "class": class_name,
                            "confidence": float(confidence)
                        })
            
            return self.counts, detections
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            raise RuntimeError(f"Frame processing failed: {str(e)}")

    def preprocess_frame(self, frame_bytes: bytes) -> np.ndarray:
        """
        Convert bytes to numpy array and preprocess for model
        """
        if not frame_bytes:
            raise ValueError("Empty frame bytes received")
            
        try:
            # Decode frame bytes to numpy array
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Failed to decode frame bytes")
                
            return frame
            
        except Exception as e:
            logger.error(f"Error preprocessing frame: {str(e)}")
            raise RuntimeError(f"Frame preprocessing failed: {str(e)}")
