import torch
from ultralytics import YOLO
import sys
import os

def convert_to_onnx(pt_path, onnx_path):
    # Load the model
    model = YOLO(pt_path)
    
    # Export the model
    model.export(format='onnx', opset=12)
    
    print(f"Model converted and saved to {onnx_path}")

if __name__ == "__main__":
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to your .pt model (assuming it's in the parent directory)
    pt_path = os.path.join(os.path.dirname(script_dir), "best.pt")
    
    # Path where the ONNX model will be saved
    onnx_path = os.path.join(script_dir, "best.onnx")
    
    convert_to_onnx(pt_path, onnx_path)
