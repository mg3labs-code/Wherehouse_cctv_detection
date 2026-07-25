# Warehouse camera videos

Put **new CCTV / warehouse videos** in this folder:

```
data/videos/
  your_new_video.mp4
```

## Run monitoring on a video

```bash
python -m src.main monitor --source "data/videos/YOUR_VIDEO.mp4"
```

## Extract training frames from a video

```bash
python extract_frames.py "data/videos/YOUR_VIDEO.mp4" 5
```

## Tips

- Supported: `.mp4`, `.avi`, `.mkv`, `.mov`
- Prefer copying files here (do not rename while the monitor is running)
- Large videos are gitignored so they stay local
