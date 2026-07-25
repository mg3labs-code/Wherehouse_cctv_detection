"""Model Training Module"""
from ultralytics import YOLO
from .config import Config
from .utils import create_data_yaml
import logging

class YOLOv8Trainer:
    """YOLOv8 Model Trainer"""
    
    def __init__(self):
        self.logger = Config.setup_logging()
    
    def train(self, data_path, model_size='m', epochs=150, batch_size=16, 
              imgsz=640, device=0):
        """Train YOLOv8 model"""
        
        # Create data.yaml
        data_yaml = create_data_yaml(data_path)
        
        self.logger.info("="*70)
        self.logger.info(f"GLS Training | Model: yolov8{model_size}")
        self.logger.info(f"Epochs: {epochs} | Batch: {batch_size}")
        self.logger.info("="*70)
        
        # Load pretrained model
        model = YOLO(f'yolov8{model_size}.pt')
        
        # Train
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=imgsz,
            device=device,
            batch=batch_size,
            lr0=Config.LEARNING_RATE,
            momentum=0.937,
            patience=Config.PATIENCE,
            cache=True,
            hsv_h=0.015,
            hsv_s=0.7,
            degrees=15,
            translate=0.15,
            scale=0.95,
            flipud=0.5,
            fliplr=0.5,
            project='runs/detect',
            name='yolov8_gls_safety'
        )
        
        self.logger.info("Training completed!")
        self.logger.info(f"Model: runs/detect/yolov8_gls_safety/weights/best.pt")
        
        return results
