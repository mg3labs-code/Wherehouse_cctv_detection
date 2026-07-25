# System Architecture

## Overview

```
Input Sources → YOLOv8 Detection → 5 Compliance Checks → Output
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                              │
│  Webcam | Video File | IP Camera | Multiple Cameras         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              YOLOv8 DETECTION LAYER                          │
│  Model: yolov8_gls_safety (7 classes)                       │
│  Output: Bounding boxes + confidence scores                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
        ▼              ▼              ▼              ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │Check 1 │  │Check 2 │  │Check 3 │  │Check 4 │
    │Conveyor│  │Harness │  │Oil Tray│  │Stopper │
    └────────┘  └────────┘  └────────┘  └────────┘
        │          │          │          │         │
        └──────────┴──────────┴──────────┴─────────┤
                                                  │
                                                  ▼
                                            ┌────────┐
                                            │Check 5 │
                                            │ Speed  │
                                            └────────┘
                                                  │
        ┌─────────────────────────────────────────┤
        │                                         │
        ▼                                         ▼
    ┌─────────┐                             ┌──────────┐
    │Violations│                             │Dashboard │
    └─────────┘                             └──────────┘
        │
    ┌───┴──────────┬──────────────┐
    │              │              │
    ▼              ▼              ▼
  LOGS          REPORTS        VIDEO
  (txt)         (JSON)          (mp4)
```

## Data Flow

```
Frame → Preprocess → YOLOv8 → Detections → Compliance Checks
                                                     │
                                    ┌────────────────┼────────────────┐
                                    │                │                │
                              Violations       Dashboard          Logging
                                    │                │                │
                              Real-time        Display            Files
                              Alerts
```

## File Structure

```
src/
├── main.py         # CLI entry point
├── config.py       # Configuration
├── trainer.py      # Model training
├── monitor.py      # Compliance checks
└── utils.py        # Utilities

config/
└── settings.yaml   # Settings

data/
└── dataset/        # Training data

outputs/
├── logs/          # Violation logs
├── reports/       # JSON reports
└── videos/        # Output videos

docs/
├── QUICK_START.md
├── SETUP_GUIDE.md
├── API.md
└── ARCHITECTURE.md

scripts/
├── train.sh
├── monitor.sh
└── setup_env.sh
```

## Processing Pipeline

### Training Pipeline

```
Dataset → Data Preparation → YOLOv8 Training → Model Evaluation → Best Model
```

### Monitoring Pipeline

```
Video Frame → Preprocess (640x640) → YOLOv8 Inference → 
5 Compliance Checks → Violation Detection → Visualization → Output
```

## Performance

- **Input:** Up to 1920x1080 resolution
- **Processing:** ~20-40 FPS (YOLOv8-M on RTX 3080)
- **Output:** Real-time dashboard + video recording
- **Latency:** ~50-100ms per frame

## Scalability

- **Single GPU:** 1 concurrent stream
- **Multi-GPU:** Multiple streams (1 per GPU)
- **Docker:** Containerized deployment
- **Cloud:** AWS EC2, GCP Compute Engine compatible
