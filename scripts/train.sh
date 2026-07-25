#!/bin/bash
# Training script

echo "GLS Warehouse Safety - Training Script"
echo "======================================="

# Check if data exists
if [ ! -d "data/dataset/images/train" ]; then
    echo "ERROR: Training data not found"
    echo "Please place images in data/dataset/images/{train,val,test}/"
    exit 1
fi

# Parse arguments
MODEL=${1:-m}
EPOCHS=${2:-150}
BATCH=${3:-16}

echo "Starting training..."
echo "Model: $MODEL | Epochs: $EPOCHS | Batch: $BATCH"

python -m src.main train \
    --data-path data/dataset \
    --model $MODEL \
    --epochs $EPOCHS \
    --batch $BATCH

echo "Training complete!"
echo "Model saved to: runs/detect/yolov8_gls_safety/weights/best.pt"
