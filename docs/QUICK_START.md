# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Prepare dataset
# Place warehouse images in data/dataset/images/{train,val,test}/
# Label with YOLO format in data/dataset/labels/{train,val,test}/
```

## Training (30 minutes to 2 hours)

```bash
python -m src.main train \
  --data-path data/dataset \
  --model m \
  --epochs 150 \
  --batch 16
```

## Monitoring

### Webcam
```bash
python -m src.main monitor --source 0
```

### Video File
```bash
python -m src.main monitor --source warehouse.mp4 --save-video
```

### IP Camera
```bash
python -m src.main monitor --source rtsp://camera:554/stream --save-video
```

## Output Files

- `outputs/logs/gls_violations.log` - Violations log
- `outputs/reports/gls_report.json` - Detailed report
- `outputs/videos/gls_output.mp4` - Marked video

## Keyboard Controls

- `q` - Quit
- `s` - Save screenshot
