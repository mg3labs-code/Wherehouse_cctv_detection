# GLS Warehouse Safety Compliance System - Project Summary

## 🎯 Project Overview

Production-ready, real-time warehouse safety compliance system using YOLOv8 deep learning.

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** January 2024

## ✅ 5 Critical Safety Checks

1. **Man Movement Near Conveyor** - Detects unsafe proximity (< 150px)
2. **Safety Harness Compliance** - Verifies protective equipment
3. **Oil Tray Presence** - Ensures spill prevention equipment
4. **Wheel Stopper Presence** - Checks vehicle parking safety
5. **Forklift Speed Monitoring** - Detects overspeeding (> 100 px/sec)

## 📁 Project Structure

```
gls-warehouse-safety-system/
├── src/                    # Main source code
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── config.py          # Configuration
│   ├── trainer.py         # Model training
│   ├── monitor.py         # Compliance monitoring
│   └── utils.py           # Utilities
│
├── data/                  # Dataset directory
│   └── dataset/
│       ├── images/        # Training images
│       │   ├── train/
│       │   ├── val/
│       │   └── test/
│       └── labels/        # YOLO format labels
│           ├── train/
│           ├── val/
│           └── test/
│
├── models/                # Pre-trained models storage
├── outputs/               # Output files
│   ├── logs/             # Violation logs
│   ├── reports/          # JSON reports
│   └── videos/           # Output videos
│
├── config/                # Configuration files
│   └── settings.yaml
│
├── docs/                  # Documentation
│   ├── QUICK_START.md
│   ├── SETUP_GUIDE.md
│   ├── API.md
│   └── ARCHITECTURE.md
│
├── scripts/               # Shell scripts
│   ├── train.sh
│   ├── monitor.sh
│   └── setup_env.sh
│
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── setup.py              # Setup configuration
├── README.md             # Project README
├── LICENSE               # MIT License
├── Dockerfile            # Docker deployment
├── docker-compose.yml    # Docker Compose
└── PROJECT_SUMMARY.md    # This file
```

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Prepare Data
```
Place warehouse images in:
data/dataset/images/{train,val,test}/
Label with YOLO format in:
data/dataset/labels/{train,val,test}/
```

### 3. Train
```bash
python -m src.main train --data-path data/dataset --epochs 150
```

### 4. Monitor
```bash
# Webcam
python -m src.main monitor --source 0

# Video
python -m src.main monitor --source warehouse.mp4 --save-video

# IP Camera
python -m src.main monitor --source rtsp://camera:554/stream --save-video
```

## 📊 System Specifications

### Hardware Requirements
- Python 3.8+
- 8GB+ RAM
- NVIDIA GPU (recommended) or CPU (slower)
- CUDA 11.0+ (for GPU)

### Software Stack
- PyTorch 2.0+
- YOLOv8 (Ultralytics)
- OpenCV 4.8+
- NumPy 1.24+

### Performance
- **Speed:** 20-40 FPS (YOLOv8-Medium)
- **Accuracy:** 75-85% mAP (with proper training)
- **Latency:** ~50-100ms per frame
- **Memory:** ~2GB GPU

## 📈 Model Options

| Model | Speed | Accuracy | FPS | Memory |
|-------|-------|----------|-----|--------|
| nano | ⚡⚡⚡ | 40-60% | 60-80 | 500MB |
| small | ⚡⚡ | 60-75% | 40-60 | 1GB |
| **medium** | ⚡ | 75-85% | 20-40 | 2GB |
| large | Slow | 80-90% | 10-20 | 3GB |
| xlarge | Slowest | 85-95% | 5-10 | 4GB |

**Recommendation:** Start with medium model

## 📋 7 Detection Classes

0. **person** - Workers
1. **forklift** - Powered equipment
2. **safety_harness** - Protective equipment
3. **oil_tray** - Spill prevention
4. **wheel_stopper** - Parking safety
5. **conveyor** - Material handling equipment
6. **goods_pallet** - Cargo

## ⚙️ Configuration

Edit `config/settings.yaml`:

```yaml
conveyor_danger_distance: 150
wheel_stopper_range: 100
forklift_speed_threshold: 100
model_confidence: 0.5
```

## 📊 Output

### Files Generated
- `outputs/logs/gls_violations.log` - Text log of all violations
- `outputs/reports/gls_report.json` - Detailed JSON report
- `outputs/videos/gls_output.mp4` - Annotated video (if --save-video)

### Dashboard
- Real-time status of 5 compliance checks
- Violation count display
- FPS counter

### Log Format
```
2024-01-15 10:23:45 - WARNING - VIOLATION: Person near conveyor (distance: 125.5)
2024-01-15 10:24:12 - WARNING - VIOLATION: No safety harness detected
```

## 🔧 Development

### Project Layout
- `src/` - All source code
- `config/` - Configuration files
- `data/` - Dataset storage
- `outputs/` - Results and logs
- `docs/` - Documentation
- `scripts/` - Utility scripts

### Entry Points
1. `src/main.py` - CLI interface
2. `scripts/train.sh` - Training script
3. `scripts/monitor.sh` - Monitoring script

### Key Classes
- `YOLOv8Trainer` - Model training
- `ComplianceMonitor` - Real-time monitoring
- `Config` - Configuration management

## 🐳 Docker Deployment

### Build
```bash
docker build -t gls-safety .
```

### Run
```bash
docker run --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  gls-safety
```

### Docker Compose
```bash
docker-compose up -d
```

## 📝 Documentation

- **README.md** - Project overview
- **docs/QUICK_START.md** - 10-minute setup
- **docs/SETUP_GUIDE.md** - Detailed installation
- **docs/API.md** - API documentation
- **docs/ARCHITECTURE.md** - System design

## 🔐 Security & Privacy

- Violations logged locally
- No external data transmission
- Encrypted report storage recommended
- GDPR-compliant design

## 📞 Support

1. Check documentation in `docs/`
2. Review logs in `outputs/logs/`
3. Check generated reports in `outputs/reports/`

## 🎓 Training Data

### Minimum Requirements
- 500+ images total
- 80% train, 12% val, 8% test
- Balanced class distribution
- Multiple angles and lighting

### Labeling Tools
- Roboflow
- LabelImg
- CVAT
- Makesense.ai

## 🚀 Production Deployment

### Single Machine
```bash
nohup python -m src.main monitor --source rtsp://camera &
```

### Cloud (AWS)
```bash
# Upload to EC2 instance with GPU
# Run monitoring continuously
```

### Multi-Camera
```bash
# Deploy separate instances per camera
# Centralized logging and reporting
```

## 📊 KPIs to Track

- Detection accuracy (mAP > 85%)
- False positive rate (< 5%)
- FPS maintained (> 20)
- Violation detection rate (trending data)
- Response time (< 1 second)

## 🔄 Maintenance

### Regular Tasks
1. Monitor violation trends
2. Update model quarterly
3. Check system logs
4. Validate accuracy metrics
5. Update training data

### Monitoring Checklist
- [ ] Model accuracy maintained
- [ ] No GPU memory issues
- [ ] Violation logs clean
- [ ] Reports generated
- [ ] Video outputs saved

## 📜 License

MIT License - See LICENSE file

## 👥 Contributors

Safety Team - 2024

## 🎯 Future Enhancements

- [ ] Email/SMS alerts
- [ ] Database integration
- [ ] Web dashboard
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Multi-site federation

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** January 2024
