import sys
import os
from pathlib import Path
import time
import cv2
import numpy as np
from ultralytics import YOLO
import json
from datetime import datetime

class DamagedBoxTester:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.results_dir = Path("tests/results")
        self.images_output_dir = self.results_dir / "images"
        self.videos_output_dir = self.results_dir / "videos"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.images_output_dir.mkdir(parents=True, exist_ok=True)
        self.videos_output_dir.mkdir(parents=True, exist_ok=True)
        
    def process_image(self, image_path, conf_threshold=0.25):
        """Process a single image and return detection results."""
        start_time = time.time()
        
        # Read and process image
        image = cv2.imread(str(image_path))
        if image is None:
            return None
        
        # Run detection
        results = self.model(image, conf=conf_threshold)[0]
        processing_time = time.time() - start_time
        
        # Get detection results
        boxes = results.boxes
        detection_results = {
            'filename': image_path.name,
            'processing_time': processing_time,
            'detections': []
        }
        
        if len(boxes) > 0:
            for box in boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                detection_results['detections'].append({
                    'class_id': class_id,
                    'confidence': confidence,
                    'bbox': box.xyxy[0].tolist()
                })
                
                # Draw bounding box on image
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"Damaged: {confidence:.2f}"
                cv2.putText(image, label, (x1, y1-10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save annotated image
        output_path = self.images_output_dir / image_path.name
        cv2.imwrite(str(output_path), image)
        
        return detection_results

    def process_video(self, video_path, conf_threshold=0.25):
        """Process a video and return detection results."""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"Error: could not open video file {video_path}")
            return

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        output_path = self.videos_output_dir / video_path.name
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Run detection
            results = self.model(frame, conf=conf_threshold)[0]

            # Get detection results
            boxes = results.boxes
            if len(boxes)> 0:
                for box in boxes:
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    # Draw bounding box on image
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"Damaged: {confidence:.2f}"
                    cv2.putText(frame, label, (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Write the frame to the output video
            out.write(frame)

        # Release everything if job is finished
        cap.release()
        out.release()
        print(f"Processd video saved to {output_path}")
    
    def test_dataset(self, damaged_dir, undamaged_dir):
        """Test the model on both damaged and undamaged images."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'damaged_images': [],
            'undamaged_images': [],
            'summary': {
                'total_damaged': 0,
                'total_undamaged': 0,
                'true_positives': 0,
                'false_positives': 0,
                'avg_confidence_damaged': 0,
                'avg_processing_time': 0
            }
        }
        
        # Process damaged images
        damaged_paths = list(Path(damaged_dir).glob('*.jpg')) + list(Path(damaged_dir).glob('*.jpeg'))
        results['summary']['total_damaged'] = len(damaged_paths)
        
        total_time = 0
        total_confidence = 0
        detected_count = 0
        
        for img_path in damaged_paths:
            detection_result = self.process_image(img_path)
            if detection_result:
                results['damaged_images'].append(detection_result)
                total_time += detection_result['processing_time']
                
                if detection_result['detections']:
                    detected_count += 1
                    total_confidence += max(d['confidence'] for d in detection_result['detections'])
        
        # Process undamaged images
        undamaged_paths = list(Path(undamaged_dir).glob('*.jpg')) + list(Path(damaged_dir).glob('*.jpeg'))
        results['summary']['total_undamaged'] = len(undamaged_paths)
        
        false_positives = 0
        for img_path in undamaged_paths:
            detection_result = self.process_image(img_path)
            if detection_result:
                results['undamaged_images'].append(detection_result)
                total_time += detection_result['processing_time']
                
                if detection_result['detections']:
                    false_positives += 1
        
        # Calculate summary statistics
        total_images = len(damaged_paths) + len(undamaged_paths)
        results['summary']['true_positives'] = detected_count
        results['summary']['false_positives'] = false_positives
        
        if detected_count > 0:
            results['summary']['avg_confidence_damaged'] = total_confidence / detected_count
            
        if total_images > 0:
            results['summary']['avg_processing_time'] = total_time / total_images
            
        # Save results to JSON file
        results_file = self.results_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        return results

def main():
    # Get the absolute path to the model file
    model_path = Path("best.pt").absolute()
    
    if not model_path.exists():
        print(f"Error: Model file not found at {model_path}")
        sys.exit(1)
    
    # Initialize tester
    tester = DamagedBoxTester(str(model_path))
    
    # Test directories
    damaged_dir = "tests/images/damaged"
    undamaged_dir = "tests/images/undamaged"
    damaged_video_dir = "tests/videos/damaged"
    
    # Run tests
    print("Starting model testing...")
    results = tester.test_dataset(damaged_dir, undamaged_dir)

    # Process undamged videos
    damaged_video_paths = list(Path(damaged_video_dir).glob('*.mp4'))
    for video_path in damaged_video_paths:
        tester.process_video(video_path)
    
    # Print summary
    print("\nTest Results Summary:")
    print(f"Total Damaged Images: {results['summary']['total_damaged']}")
    print(f"Total Undamaged Images: {results['summary']['total_undamaged']}")
    print(f"True Positives: {results['summary']['true_positives']}")
    print(f"False Positives: {results['summary']['false_positives']}")
    print(f"Average Confidence (Damaged): {results['summary']['avg_confidence_damaged']:.2f}")
    print(f"Average Processing Time: {results['summary']['avg_processing_time']:.3f} seconds")

if __name__ == "__main__":
    main()
