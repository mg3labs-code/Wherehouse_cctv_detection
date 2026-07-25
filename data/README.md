# Dataset Directory

Place your warehouse images and labels here.

## Structure

```
data/dataset/
├── images/
│   ├── train/   (400+ images - 80%)
│   ├── val/     (60+ images - 12%)
│   └── test/    (40+ images - 8%)
└── labels/      (YOLO format .txt files)
    ├── train/
    ├── val/
    └── test/
```

## Preparation Steps

1. **Collect Images**
   - Take warehouse photos
   - Capture different angles, lighting, scenarios

2. **Label Images**
   - Use Roboflow, LabelImg, or CVAT
   - Label 7 classes:
     - 0: person
     - 1: forklift
     - 2: safety_harness
     - 3: oil_tray
     - 4: wheel_stopper
     - 5: conveyor
     - 6: goods_pallet

3. **Export Format**
   - Export in YOLO format
   - Format: `<class_id> <x_center> <y_center> <width> <height>`

4. **Organize Files**
   - Copy images to appropriate train/val/test folders
   - Copy labels to corresponding label folders

## Minimum Requirements

- 500+ total images
- Balanced across classes
- 80% train, 12% val, 8% test split
- High quality, diverse scenarios
