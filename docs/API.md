# API Documentation

## ComplianceMonitor

### Initialize

```python
from src.monitor import ComplianceMonitor

monitor = ComplianceMonitor('model_path.pt')
```

### Process Frame

```python
result_frame, violations = monitor.process_frame(frame)
```

### Save Report

```python
monitor.save_report('path/to/report.json')
```

## YOLOv8Trainer

### Initialize

```python
from src.trainer import YOLOv8Trainer

trainer = YOLOv8Trainer()
```

### Train Model

```python
results = trainer.train(
    data_path='data/dataset',
    model_size='m',
    epochs=150,
    batch_size=16
)
```

## Config

```python
from src.config import Config

# Access configuration
Config.CONVEYOR_DANGER_DISTANCE
Config.FORKLIFT_SPEED_THRESHOLD
Config.MODEL_CONFIDENCE
```

## Utilities

```python
from src.utils import (
    create_data_yaml,
    calculate_distance,
    get_bbox_center,
    check_overlap
)
```
