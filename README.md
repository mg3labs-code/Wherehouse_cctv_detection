# GLS Warehouse Safety Compliance System

Real-time YOLOv8-based detection system for warehouse safety compliance with 5 critical checks.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Train model on your data
python src/main.py train --data-path data/dataset --epochs 150

# Run real-time monitoring (OpenCV window)
python src/main.py monitor --source 0
```

## 🖥️ Production Web Dashboard

SIERA-style analytics UI connected to the YOLO backend.

```bash
# Terminal 1 — API on port 8001 (8000 may be used by another GLS app)
python run_api.py

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

- Safety Analytics KPIs + charts (SQLite event store)
- Live Monitor (start/stop video, MJPEG stream, auto-logs violations)
- Reports / Assets pages

API docs: `http://localhost:8001/docs`

> **Note:** If the UI is blank, another service is likely on port 8000. This project’s API uses **8001**. Restart `npm run dev` after changing the proxy.

## 📋 Features

✅ Man Movement Near Conveyor Detection
✅ Safety Harness Compliance Verification
✅ Oil Tray Presence Monitoring
✅ Wheel Stopper Presence Detection
✅ Forklift Speed Monitoring

## 📁 Project Structure

```
gls-warehouse-safety-system/
├── src/                    # Main source code
│   ├── main.py            # Entry point
│   ├── config.py          # Configuration
│   ├── trainer.py         # Model training
│   ├── monitor.py         # Real-time monitoring
│   └── utils.py           # Utility functions
│
├── data/                  # Dataset directory
│   └── dataset/
│       ├── images/        # Training images
│       └── labels/        # YOLO format labels
│
├── models/                # Trained models storage
├── outputs/               # Output files
│   ├── logs/             # Violation logs
│   ├── reports/          # JSON reports
│   └── videos/           # Output videos
│
├── config/                # Configuration files
├── docs/                  # Documentation
├── scripts/               # Shell scripts
├── tests/                 # Unit tests
│
├── requirements.txt       # Python dependencies
├── setup.py              # Setup configuration
└── README.md             # This file
```

## 🎯 5 Compliance Checks

### 1. Man Movement Near Conveyor
- Detects when workers get too close (< 150px)
- Alert: RED box + voice/visual alert

### 2. Safety Harness Compliance
- Verifies worker is wearing safety harness
- Alert: RED frame if not detected

### 3. Oil Tray Presence
- Checks for spill prevention equipment
- Alert: ORANGE alert if missing

### 4. Wheel Stopper Presence
- Ensures parked vehicles have wheel stoppers
- Alert: BLUE alert if missing

### 5. Forklift Speed Monitoring
- Detects overspeeding forklifts (> 100 px/sec)
- Alert: RED alert if exceeded

## 📊 Configuration

Edit `config/settings.yaml` to adjust thresholds:

```yaml
CONVEYOR_DANGER_DISTANCE: 150      # pixels
WHEEL_STOPPER_RANGE: 100            # pixels
FORKLIFT_SPEED_THRESHOLD: 100       # pixels/second
MODEL_CONFIDENCE: 0.5               # Detection confidence
```

## 📈 Usage Examples

### Training
```bash
python src/main.py train \
  --data-path data/dataset \
  --model m \
  --epochs 150 \
  --batch 16
```

### Monitoring from Webcam
```bash
python src/main.py monitor --source 0
```

### Monitoring from Video
```bash
python src/main.py monitor \
  --source warehouse.mp4 \
  --save-video
```

### Monitoring from IP Camera
```bash
python src/main.py monitor \
  --source rtsp://camera:554/stream \
  --save-video
```

## 📊 Output Files

- `outputs/logs/gls_violations.log` - Violation log
- `outputs/reports/gls_report.json` - Detailed report
- `outputs/videos/gls_output.mp4` - Marked video

## 🔧 Performance

| Model | Speed | Accuracy | FPS |
|-------|-------|----------|-----|
| nano | ⚡⚡⚡ | 40-60% | 60-80 |
| small | ⚡⚡ | 60-75% | 40-60 |
| **medium** | ⚡ | 75-85% | 20-40 |
| large | Slow | 80-90% | 10-20 |

## 📝 Data Format

Training data should be organized as:

```
data/dataset/
├── images/
│   ├── train/   (400+ images)
│   ├── val/     (60+ images)
│   └── test/    (40+ images)
└── labels/      (YOLO format .txt files)
```

Labels format (YOLO):
```
<class_id> <x_center> <y_center> <width> <height>
```

Classes:
- 0: person
- 1: forklift
- 2: safety_harness
- 3: oil_tray
- 4: wheel_stopper
- 5: conveyor
- 6: goods_pallet

## 🛠️ Installation

### Requirements
- Python 3.8+
- NVIDIA GPU (recommended, CPU supported)
- CUDA 11.0+ (for GPU)

### Setup

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Prepare dataset in `data/dataset/`
4. Train model: `python src/main.py train`
5. Run monitoring: `python src/main.py monitor`

## 📚 Documentation

See `docs/` folder for detailed guides:
- `QUICK_START.md` - Quick setup guide
- `SETUP_GUIDE.md` - Detailed setup
- `ARCHITECTURE.md` - System architecture
- `API.md` - API documentation

## 🎮 Controls

During monitoring:
- `q` - Quit
- `s` - Save screenshot
- `p` - Pause/Resume

## 🤝 Support

For issues or questions, check:
1. `docs/QUICK_START.md`
2. `docs/SETUP_GUIDE.md`
3. Logs in `outputs/logs/`

## 📜 License

MIT License - See LICENSE file

## 🔐 Security

- Violations are logged to local files
- No data is sent externally by default
- Encrypt reports before sharing

## 📞 Contact

Safety Team: safety@warehouse.com

---

**Version:** 1.0
**Status:** Production Ready
**Last Updated:** January 2024
