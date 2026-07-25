# Complete Setup Guide

## Phase 1: Environment Setup

### System Requirements
- Python 3.8+
- NVIDIA GPU (recommended)
- CUDA 11.0+ (for GPU)
- 8GB+ RAM

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

## Phase 2: Data Preparation

### Dataset Structure

```
data/dataset/
├── images/
│   ├── train/   (400+ images)
│   ├── val/     (60+ images)
│   └── test/    (40+ images)
└── labels/      (YOLO format)
```

### Labeling

1. Collect warehouse images
2. Label 7 classes using Roboflow, LabelImg, or CVAT
3. Export in YOLO format
4. Place in appropriate folders

### YOLO Format

```
<class_id> <x_center> <y_center> <width> <height>

Classes:
0 - person
1 - forklift
2 - safety_harness
3 - oil_tray
4 - wheel_stopper
5 - conveyor
6 - goods_pallet
```

## Phase 3: Model Training

### Basic Training

```bash
python -m src.main train --data-path data/dataset
```

### Advanced Training

```bash
python -m src.main train \
  --data-path data/dataset \
  --model l \
  --epochs 200 \
  --batch 32 \
  --imgsz 640 \
  --device 0
```

### Model Sizes

- `n` (nano) - Fast, lower accuracy
- `s` (small) - Balanced
- `m` (medium) - **Recommended**
- `l` (large) - Slower, higher accuracy
- `x` (xlarge) - Slowest, highest accuracy

## Phase 4: Deployment

### Real-Time Monitoring

```bash
python -m src.main monitor --source 0 --save-video
```

### Configuration

Edit `src/config.py`:

```python
CONVEYOR_DANGER_DISTANCE = 150
WHEEL_STOPPER_RANGE = 100
FORKLIFT_SPEED_THRESHOLD = 100
MODEL_CONFIDENCE = 0.5
```

### Output Monitoring

```bash
# Watch violations
tail -f outputs/logs/gls_violations.log

# View reports
cat outputs/reports/gls_report.json
```

## Troubleshooting

### Low Accuracy
- Add more training data
- Increase epochs
- Use larger model

### Low FPS
- Use smaller model (nano/small)
- Reduce resolution
- Enable GPU

### Memory Issues
- Reduce batch size
- Use smaller model
- Reduce image resolution
