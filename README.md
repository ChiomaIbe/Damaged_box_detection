# Damaged Box Detection System

## Overview
This project implements a real-time damaged box detection system using computer vision and deep learning. It combines YOLOv8 object detection with a modern web interface to provide instant feedback on package conditions through webcam feeds.

## System Requirements

### Backend Requirements
- Python 3.8+
- FastAPI
- ONNX Runtime
- OpenCV
- PyTorch
- Additional dependencies listed in `backend/requirements.txt`

### Frontend Requirements
- Node.js 14+
- React.js
- WebRTC capabilities
- Modern web browser with camera access

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Damaged_box_detection
```

2. Set up the backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Configure environment variables:
   - Copy `.env.example` to `.env` in the frontend directory
   - Adjust API endpoints if needed

## Usage

1. Start the backend server:
```bash
cd backend
python main.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Access the application at `http://localhost:3000`

## Project Structure

```
Damaged_box_detection/
├── backend/
│   ├── models/          # ML model implementations
│   ├── routers/         # API endpoints
│   ├── main.py         # Server entry point
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/ # React components
│   │   └── App.js      # Main application
│   └── package.json    # Node.js dependencies
└── tests/
    ├── images/         # Test image datasets
    ├── videos/         # Test video datasets
    └── results/        # Test results and metrics
```

## Features

- Real-time box damage detection through webcam
- Support for image and video file processing
- REST API for detection requests
- Web interface with live preview
- Detection result visualization
- Performance metrics tracking

## Testing

1. Run backend tests:
```bash
cd tests
python test_model.py
python test_onnx_model.py
```

2. View test results in the `tests/results/` directory

## Technologies Used

- **Backend:**
  - FastAPI (Python web framework)
  - ONNX Runtime (ML model optimization)
  - OpenCV (Image processing)
  - YOLOv8 (Object detection)

- **Frontend:**
  - React.js (UI framework)
  - WebRTC (Camera stream handling)
  - Axios (API client)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

## Acknowledgments

- YOLOv8 team for the object detection model
- FastAPI team for the backend framework
- React team for the frontend framework
