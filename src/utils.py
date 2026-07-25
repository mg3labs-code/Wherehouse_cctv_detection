"""Utility Functions"""
import numpy as np
import cv2
import os
import yaml

def create_data_yaml(data_path):
    """Create data.yaml for YOLOv8"""
    from .config import Config
    
    yaml_data = {
        'path': os.path.abspath(data_path),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': 7,
        'names': list(Config.CLASSES.values())
    }
    
    yaml_path = os.path.join(data_path, 'data.yaml')
    os.makedirs(data_path, exist_ok=True)
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_data, f)
    
    return yaml_path

def ensure_directories():
    """Ensure all required directories exist"""
    dirs = [
        'outputs/logs',
        'outputs/reports',
        'outputs/videos',
        'models'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def calculate_distance(point1, point2):
    """Calculate Euclidean distance"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def get_bbox_center(bbox):
    """Get center of bounding box"""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def check_overlap(box1, box2):
    """Check if two boxes overlap"""
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    return not (x1_max < x2_min or x2_max < x1_min or 
                y1_max < y2_min or y2_max < y1_min)


def detect_yellow_aisle_lines(frame, max_lines=2):
    """
    Detect warehouse aisle ROAD WAY yellow floor paint as left/right polylines.

    Tracks painted lines on the concrete (inward of rack toes), not cardboard
    on rack faces. Always returns Left + Right when possible.
    """
    h, w = frame.shape[:2]
    y0 = int(h * 0.24)
    floor = frame[y0:h, :]
    fh, fw = floor.shape[:2]
    mid = fw // 2

    hsv = cv2.cvtColor(floor, cv2.COLOR_BGR2HSV)
    # Floor paint: yellow but not deep brown cardboard
    mask = cv2.inRange(hsv, (15, 28, 55), (40, 200, 255))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 3), np.uint8))

    # Floor trapezoid — stay on concrete, cut off rack faces / box stacks
    trap = np.zeros_like(mask)
    top_half = int(fw * 0.17)
    bot_half = int(fw * 0.38)
    cv2.fillPoly(trap, [np.array([
        [mid - top_half, 0],
        [mid + top_half, 0],
        [mid + bot_half, fh - 1],
        [mid - bot_half, fh - 1],
    ], dtype=np.int32)], 255)
    mask = cv2.bitwise_and(mask, trap)

    # Drop wide cardboard blobs; keep thin floor strokes
    n_cc, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    clean = np.zeros_like(mask)
    for i in range(1, n_cc):
        area = int(stats[i, cv2.CC_STAT_AREA])
        bw = int(stats[i, cv2.CC_STAT_WIDTH])
        bh = int(stats[i, cv2.CC_STAT_HEIGHT])
        if area < 20 or area > fw * fh * 0.10:
            continue
        if bw > max(40, int(fw * 0.10)) and bh < bw * 0.6:
            continue
        clean[labels == i] = 255

    band_h = max(6, fh // 50)
    left_pts, right_pts = [], []

    for y in range(fh - band_h, max(band_h, int(fh * 0.03)), -band_h):
        col = (clean[y - band_h:y] > 0).sum(axis=0).astype(np.int32)
        cy = y0 + y - band_h // 2
        t = 1.0 - (y / float(max(fh - 1, 1)))  # 0 bottom → 1 top

        # Paint windows on floor near rack toes (NOT into rack faces)
        l0 = mid - int(fw * (0.34 - 0.10 * t))
        l1 = mid - int(fw * (0.08 + 0.03 * t))
        r0 = mid + int(fw * (0.08 + 0.03 * t))
        r1 = mid + int(fw * (0.34 - 0.10 * t))
        l0, l1 = max(0, l0), min(mid - 4, l1)
        r0, r1 = max(mid + 4, r0), min(fw - 1, r1)

        lx = rx = None
        if l1 > l0 + 6:
            region = col[l0:l1]
            if region.max() >= 2:
                peak = l0 + int(np.argmax(region))
                # Inner edge of paint stroke (toward aisle) — avoids rack base
                thr = max(2, int(region.max() * 0.35))
                hits = np.where(region >= thr)[0]
                lx = l0 + int(hits[-1]) if len(hits) else peak
                # Sit on concrete just inside rack toe
                lx = min(l1 - 1, lx + int(fw * 0.022))

        if r1 > r0 + 6:
            region = col[r0:r1]
            if region.max() >= 2:
                # Prefer strongest paint peak, slight inward nudge onto floor
                rx = r0 + int(np.argmax(region))
                rx = max(r0 + 1, rx - int(fw * 0.010))

        if lx is not None:
            left_pts.append((lx, cy))
        if rx is not None:
            right_pts.append((rx, cy))

    def fit_road_edge(pts, side):
        """Fit near-camera floor paint, extend full aisle depth on the floor plane."""
        if len(pts) < 5:
            return None
        pts = np.array(pts, dtype=np.float32)
        pts = pts[np.argsort(pts[:, 1])]

        y_cut = y0 + int(fh * 0.40)
        near = pts[pts[:, 1] >= y_cut]
        if len(near) < 5:
            near = pts[pts[:, 1] >= (y0 + int(fh * 0.22))]
        if len(near) < 5:
            near = pts
        if len(near) < 5:
            return None

        cleaned = [near[-1]]
        for p in near[-2::-1]:
            prev = cleaned[-1]
            dx = abs(float(p[0] - prev[0]))
            dy = abs(float(p[1] - prev[1])) + 1e-6
            if dx / dy > 1.8 and dx > 22:
                continue
            cleaned.append(p)
        near = np.array(cleaned[::-1], dtype=np.float32)
        if len(near) < 5:
            return None

        ys, xs = near[:, 1], near[:, 0]
        # Bottom paint locks lateral position; use lower aisle for x_bot
        y_bot_band = y0 + int(fh * 0.45)
        bot_mask = ys >= y_bot_band
        if int(bot_mask.sum()) >= 4:
            x_bot = float(np.median(xs[bot_mask]))
        else:
            x_bot = float(np.median(xs))

        if side == 'left' and not (w * 0.18 < x_bot < w * 0.42):
            return None
        if side == 'right' and not (w * 0.58 < x_bot < w * 0.82):
            return None

        # Perspective: floor edges converge to a vanishing point near top-center.
        # This keeps polylines on the floor plane instead of cutting rack faces.
        vp_x = float(mid)
        vp_y = float(h * 0.10)
        y_max = float(h - 4)
        y_min = max(float(h * 0.14), float(y0 + 2))
        # How far toward VP at the far end (not fully to VP — leave corridor open)
        far_blend = 0.55
        x_far = x_bot + (vp_x - x_bot) * far_blend * ((y_max - y_min) / max(y_max - vp_y, 1.0))
        # Clamp far point still on correct half
        if side == 'left':
            x_far = float(np.clip(x_far, w * 0.22, mid - w * 0.06))
        else:
            x_far = float(np.clip(x_far, mid + w * 0.06, w * 0.78))

        a = (x_bot - x_far) / max(y_max - y_min, 1.0)
        b = x_bot - a * y_max

        ys_s = np.linspace(y_min, y_max, num=40)
        xs_s = np.clip(a * ys_s + b, 0, w - 1)
        poly = [(int(round(x)), int(round(y))) for x, y in zip(xs_s, ys_s)]
        conf = float(np.clip(0.70 + (ys.max() - ys.min()) / max(fh, 1) * 0.25, 0.70, 0.95))

        return {
            'points': poly,
            'polyline': True,
            'bbox': np.array([
                float(np.min(xs_s)), float(np.min(ys_s)),
                float(np.max(xs_s)), float(np.max(ys_s)),
            ], dtype=float),
            'conf': conf,
            'raw_name': 'yellow_line',
            'side': side,
            'slope': float(a),
            'intercept': float(b),
        }

    def mirror_from(src, side):
        if src is None:
            return None
        a = abs(float(src.get('slope', 0.08)))
        a = float(np.clip(a, 0.05, 0.14))
        x_bot = float(src.get('slope', 0.0)) * float(h - 10) + float(src.get('intercept', 0.0))
        gap = w * 0.36
        if side == 'right':
            a2, x_bot2 = a, min(w * 0.82, x_bot + gap)
        else:
            a2, x_bot2 = -a, max(w * 0.18, x_bot - gap)
        b2 = x_bot2 - a2 * float(h - 10)
        y_max = h - 4
        y_min = max(int(h * 0.14), y0 + 2)
        ys_s = np.linspace(y_min, y_max, num=40)
        xs_s = np.clip(a2 * ys_s + b2, 0, w - 1)
        return {
            'points': [(int(round(x)), int(round(y))) for x, y in zip(xs_s, ys_s)],
            'polyline': True,
            'bbox': np.array([
                float(np.min(xs_s)), float(np.min(ys_s)),
                float(np.max(xs_s)), float(np.max(ys_s)),
            ], dtype=float),
            'conf': 0.70,
            'raw_name': 'yellow_line',
            'side': side,
            'slope': float(a2),
            'intercept': float(b2),
            'synthetic': True,
        }

    left = fit_road_edge(left_pts, 'left')
    right = fit_road_edge(right_pts, 'right')
    if left is None and right is not None:
        left = mirror_from(right, 'left')
    if right is None and left is not None:
        right = mirror_from(left, 'right')

    results = []
    if left:
        results.append(left)
    if right:
        results.append(right)
    return results[:max_lines]


def detect_safe_route_lines(frame, max_lines=2):
    """
    Detect Safe Route Left/Right for GODOWN NO-3.

    Reuses aisle road-way geometry (floor paint + VP) so Left sits on the
    left road-way at the rack toe — not mid-aisle and not through boxes.
    Right follows the same yellow floor paint used by Aisle Road Way.
    """
    lines = detect_yellow_aisle_lines(frame, max_lines=max_lines)
    h, w = frame.shape[:2]
    mid = w // 2
    y0 = int(h * 0.24)

    def rebuild_left(x_bot, conf=0.90, synthetic=False):
        """Floor-plane left road-way from a locked bottom x."""
        x_bot = float(np.clip(x_bot, w * 0.28, w * 0.34))
        vp_x = float(mid)
        vp_y = float(h * 0.10)
        y_max = float(h - 4)
        y_min = max(float(h * 0.14), float(y0 + 2))
        far_blend = 0.55
        x_far = x_bot + (vp_x - x_bot) * far_blend * ((y_max - y_min) / max(y_max - vp_y, 1.0))
        x_far = float(np.clip(x_far, w * 0.24, mid - w * 0.06))
        a = (x_bot - x_far) / max(y_max - y_min, 1.0)
        b = x_bot - a * y_max
        ys_s = np.linspace(y_min, y_max, num=48)
        xs_s = np.clip(a * ys_s + b, 0, w - 1)
        return {
            'points': [(int(round(x)), int(round(y))) for x, y in zip(xs_s, ys_s)],
            'polyline': True,
            'bbox': np.array([
                float(np.min(xs_s)), float(np.min(ys_s)),
                float(np.max(xs_s)), float(np.max(ys_s)),
            ], dtype=float),
            'conf': float(conf),
            'raw_name': 'safe_route_line',
            'side': 'left',
            'slope': float(a),
            'intercept': float(b),
            'synthetic': bool(synthetic),
        }

    out = []
    right_ln = None
    left_src = None
    for ln in lines:
        ln = dict(ln)
        ln['raw_name'] = 'safe_route_line'
        side = ln.get('side')
        pts = ln.get('points') or []
        if not pts:
            continue
        x_bot = int(pts[-1][0])
        if side == 'right' and (w * 0.60 < x_bot < w * 0.86):
            right_ln = ln
            out.append(ln)
        elif side == 'left':
            left_src = ln

    # Aisle Left sits slightly into the open floor; pull onto left rack-toe road-way
    if left_src is not None:
        x_bot = float(left_src['points'][-1][0]) - float(w * 0.028)
        out.insert(0, rebuild_left(x_bot, conf=0.92, synthetic=False))
    elif right_ln is not None:
        # Camera is not mid-symmetric — use measured aisle span from right paint
        x_right = float(right_ln['slope']) * float(h - 6) + float(right_ln['intercept'])
        out.insert(0, rebuild_left(x_right - w * 0.44, conf=0.82, synthetic=True))

    return out[:max_lines]

