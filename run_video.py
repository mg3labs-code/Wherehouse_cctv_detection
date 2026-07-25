"""List and run monitoring on videos in data/videos/."""
import os
import sys
import glob
import subprocess

VIDEO_DIR = os.path.join("data", "videos")
EXTS = (".mp4", ".avi", ".mkv", ".mov")


def list_videos():
    os.makedirs(VIDEO_DIR, exist_ok=True)
    files = []
    for ext in EXTS:
        files.extend(glob.glob(os.path.join(VIDEO_DIR, f"*{ext}")))
    return sorted(files)


def print_list(videos):
    print("Videos in data/videos/:")
    for i, path in enumerate(videos, 1):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  {i}. {os.path.basename(path)}  ({size_mb:.1f} MB)")
    sys.stdout.flush()


def main():
    videos = list_videos()
    if not videos:
        print(f"No videos found in {VIDEO_DIR}/")
        print("Copy your new .mp4 files into that folder, then run again.")
        return

    if len(sys.argv) < 2:
        print_list(videos)
        print("\nUsage:")
        print("  python run_video.py <number>          # run monitor on that video")
        print("  python run_video.py <number> --save   # also save output video")
        print(f'  python -m src.main monitor --source "data/videos/YOUR_FILE.mp4"')
        return

    try:
        idx = int(sys.argv[1]) - 1
    except ValueError:
        print_list(videos)
        print("\nPass a video number from the list above.")
        return

    if idx < 0 or idx >= len(videos):
        print_list(videos)
        print(f"\nInvalid video number: {sys.argv[1]}")
        return

    path = videos[idx]
    print(f"Running video {idx + 1}: {os.path.basename(path)}")
    print("Loading YOLO26 model (first run can take ~15s)...")
    print("A window will open — press q to quit, s for screenshot.")
    sys.stdout.flush()

    cmd = [sys.executable, "-u", "-m", "src.main", "monitor", "--source", path]
    # Optional: python run_video.py 3 --model yolo26s.pt
    if "--model" in sys.argv:
        mi = sys.argv.index("--model")
        if mi + 1 < len(sys.argv):
            cmd.extend(["--model", sys.argv[mi + 1]])
    if "--save" in sys.argv:
        cmd.append("--save-video")
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
