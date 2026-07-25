"""Extract frames from warehouse video for training dataset"""
import cv2
import os
from pathlib import Path

def extract_frames(video_path, output_dir, frame_interval=5):
    """
    Extract frames from video
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        frame_interval: Extract every Nth frame (e.g., 5 = every 5 frames)
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Video: {video_path}")
    print(f"Total frames: {total_frames}")
    print(f"FPS: {fps}")
    print(f"Extracting every {frame_interval} frames...")
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Extract every Nth frame
        if frame_count % frame_interval == 0:
            filename = os.path.join(output_dir, f"frame_{saved_count:06d}.jpg")
            cv2.imwrite(filename, frame)
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"✓ Extracted {saved_count} frames to {output_dir}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_frames.py <video_path> [frame_interval]")
        print('Example: python extract_frames.py "data/videos/warehouse.mp4" 5')
        sys.exit(1)
    
    video_path = sys.argv[1]
    frame_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Extract to data/dataset/images/train/
    output_dir = 'data/dataset/images/train'
    
    extract_frames(video_path, output_dir, frame_interval)