"""Professional GLS Warehouse Safety Monitor dashboard overlays."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


# BGR colors matching the reference UI
COLOR_WORKER = (255, 180, 60)      # light blue-ish label style -> use cyan-blue
COLOR_WORKER_BOX = (230, 140, 20)  # blue worker boxes (BGR)
COLOR_FORKLIFT = (255, 0, 180)     # purple / magenta
COLOR_BOX = (80, 220, 80)          # green
COLOR_LINE = (0, 220, 255)         # yellow aisle line
COLOR_UNSAFE = (40, 40, 220)       # red
COLOR_WARN = (0, 200, 255)         # yellow/amber
COLOR_PANEL_BG = (28, 28, 28)
COLOR_PANEL_BORDER = (70, 70, 70)
COLOR_TEXT = (245, 245, 245)
COLOR_MUTED = (180, 180, 180)
COLOR_ALERT = (50, 50, 230)
COLOR_OK = (60, 200, 80)


def _scale(frame: np.ndarray) -> float:
    return max(0.55, min(frame.shape[1] / 1600.0, 1.4))


def _panel(img: np.ndarray, x1: int, y1: int, x2: int, y2: int, alpha: float = 0.72) -> None:
    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), COLOR_PANEL_BG, -1)
    cv2.rectangle(overlay, (x1, y1), (x2, y2), COLOR_PANEL_BORDER, 2)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)


def _text(img, text, org, scale=0.55, color=COLOR_TEXT, thick=1):
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def _draw_labeled_box(img, bbox, label, color, thickness=2):
    x1, y1, x2, y2 = map(int, bbox)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
    fs, thick = 0.82, 2
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
    ty = max(0, y1 - th - 12)
    cv2.rectangle(img, (x1, ty), (x1 + tw + 12, y1), color, -1)
    _text(img, label, (x1 + 6, y1 - 8), fs, (255, 255, 255), thick)


def _draw_pie(img, cx, cy, radius, segments: List[Tuple[float, Tuple[int, int, int]]]):
    """segments = list of (fraction 0-1, BGR color)."""
    if not segments:
        return
    start = -90
    for frac, color in segments:
        if frac <= 0:
            continue
        span = int(360 * frac)
        if span < 1:
            continue
        cv2.ellipse(img, (cx, cy), (radius, radius), 0, start, start + span, color, -1)
        start += span
    cv2.circle(img, (cx, cy), int(radius * 0.45), COLOR_PANEL_BG, -1)


def draw_title_bar(img: np.ndarray, title: str = "Hypervis Warehouse Safety Monitor - AI Powered") -> None:
    s = _scale(img)
    h = int(42 * s)
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (img.shape[1], h), (18, 18, 18), -1)
    cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)
    _text(img, title, (int(14 * s), int(28 * s)), 0.7 * s, COLOR_TEXT, 2)


def draw_unsafe_zone(img: np.ndarray, bbox, label: str = "Unsafe Zone - Keep Clear") -> None:
    x1, y1, x2, y2 = map(int, bbox)
    # Floor zone under / around object
    zw = int((x2 - x1) * 1.6)
    zh = int((y2 - y1) * 0.55)
    cx = (x1 + x2) // 2
    zy2 = min(img.shape[0] - 1, y2 + int(zh * 0.15))
    zy1 = max(0, zy2 - zh)
    zx1 = max(0, cx - zw // 2)
    zx2 = min(img.shape[1] - 1, cx + zw // 2)
    overlay = img.copy()
    cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), COLOR_UNSAFE, -1)
    cv2.addWeighted(overlay, 0.28, img, 0.72, 0, img)
    cv2.rectangle(img, (zx1, zy1), (zx2, zy2), COLOR_UNSAFE, 2)
    fs = 0.85
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fs, 2)
    tx = zx1 + 8
    ty = zy1 + th + 12
    cv2.rectangle(img, (tx - 4, ty - th - 8), (tx + tw + 8, ty + 8), (20, 20, 140), -1)
    _text(img, label, (tx, ty), fs, (220, 220, 255), 2)


def draw_high_risk_marker(img: np.ndarray, x: int, y: int, text: str) -> None:
    s = _scale(img)
    w, h = int(340 * s), int(78 * s)
    _panel(img, x, y, x + w, y + h, 0.72)
    cv2.rectangle(img, (x, y), (x + w, y + h), COLOR_WARN, 2)
    _text(img, "HIGH RISK AREA", (x + 12, y + int(30 * s)), 0.80 * s, COLOR_WARN, 2)
    _text(img, text, (x + 12, y + int(60 * s)), 0.70 * s, COLOR_TEXT, 2)


def draw_live_summary(img: np.ndarray, stats: Dict) -> None:
    s = _scale(img)
    x1, y1 = int(12 * s), int(52 * s)
    x2, y2 = int(400 * s), int(390 * s)
    _panel(img, x1, y1, x2, y2)
    _text(img, "Live Safety Summary", (x1 + 14, y1 + int(30 * s)), 0.78 * s, COLOR_TEXT, 2)

    rows = [
        ("Total Detections", stats.get("total", 0), COLOR_TEXT),
        ("Workers Detected", stats.get("workers", 0), COLOR_WORKER_BOX),
        ("No Helmet", stats.get("no_helmet", 0), COLOR_ALERT if stats.get("no_helmet", 0) else COLOR_OK),
        ("No Vest", stats.get("no_vest", 0), COLOR_WARN if stats.get("no_vest", 0) else COLOR_OK),
        ("Forklifts", stats.get("forklifts", 0), COLOR_FORKLIFT),
        (
            "Forklift Speed",
            (
                f"{float(stats.get('forklift_speed_kmh', 0)):.1f} km/h"
                if stats.get("forklifts", 0)
                else "—"
            ),
            COLOR_ALERT if stats.get("forklift_overspeed") else COLOR_FORKLIFT,
        ),
        ("Road Ways", stats.get("yellow_lines", 0), COLOR_LINE),
        ("PPE Compliance", f"{stats.get('ppe_pct', 100)}%", COLOR_OK if stats.get("ppe_pct", 100) >= 80 else COLOR_WARN),
    ]
    y = y1 + int(62 * s)
    for name, val, color in rows:
        _text(img, name, (x1 + 16, y), 0.62 * s, COLOR_MUTED, 2)
        val_s = str(val)
        # right-align value inside panel
        (tw, _), _ = cv2.getTextSize(val_s, cv2.FONT_HERSHEY_SIMPLEX, 0.68 * s, 2)
        _text(img, val_s, (x2 - tw - int(14 * s), y), 0.68 * s, color, 2)
        y += int(36 * s)


def draw_safety_alert(img: np.ndarray, alert: Optional[Dict]) -> None:
    s = _scale(img)
    w = img.shape[1]
    pw, ph = int(310 * s), int(120 * s)
    x2, y1 = w - int(12 * s), int(52 * s)
    x1, y2 = x2 - pw, y1 + ph
    if not alert:
        _panel(img, x1, y1, x2, y2, 0.65)
        _text(img, "SAFETY STATUS", (x1 + 12, y1 + int(28 * s)), 0.55 * s, COLOR_OK, 2)
        _text(img, "All Clear", (x1 + 12, y1 + int(62 * s)), 0.7 * s, COLOR_OK, 2)
        _text(img, datetime.now().strftime("%H:%M:%S"), (x1 + 12, y1 + int(95 * s)), 0.45 * s, COLOR_MUTED, 1)
        return

    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (30, 30, 160), -1)
    cv2.addWeighted(overlay, 0.78, img, 0.22, 0, img)
    cv2.rectangle(img, (x1, y1), (x2, y2), COLOR_ALERT, 2)
    _text(img, "SAFETY ALERT", (x1 + 12, y1 + int(28 * s)), 0.6 * s, (220, 220, 255), 2)
    _text(img, alert.get("title", "Violation"), (x1 + 12, y1 + int(58 * s)), 0.65 * s, COLOR_TEXT, 2)
    _text(img, f"Location: {alert.get('location', 'Aisle')}", (x1 + 12, y1 + int(85 * s)), 0.42 * s, COLOR_MUTED, 1)
    _text(img, alert.get("time", datetime.now().strftime("%H:%M:%S")), (x1 + 12, y1 + int(108 * s)), 0.42 * s, COLOR_MUTED, 1)


def draw_compliance_pie(img: np.ndarray, stats: Dict) -> None:
    s = _scale(img)
    h = img.shape[0]
    x1, y2 = int(12 * s), h - int(12 * s)
    x2, y1 = int(380 * s), y2 - int(230 * s)
    _panel(img, x1, y1, x2, y2)
    _text(img, "Safety Compliance", (x1 + 14, y1 + int(30 * s)), 0.72 * s, COLOR_TEXT, 2)

    compliant = max(0.0, min(1.0, stats.get("ppe_pct", 100) / 100.0))
    no_helmet = stats.get("no_helmet", 0)
    no_vest = stats.get("no_vest", 0)
    workers = max(1, stats.get("workers", 1))
    nh = (no_helmet / workers) * (1 - compliant) if workers else 0
    nv = (no_vest / workers) * (1 - compliant) if workers else 0
    # Normalize remaining gap
    other = max(0.0, 1.0 - compliant)
    if no_helmet + no_vest > 0:
        nh = other * (no_helmet / (no_helmet + no_vest))
        nv = other * (no_vest / (no_helmet + no_vest))
    else:
        nh, nv = 0.0, other

    cx = x1 + int(100 * s)
    cy = y1 + int(130 * s)
    _draw_pie(img, cx, cy, int(62 * s), [
        (compliant, COLOR_OK),
        (nh, COLOR_ALERT),
        (nv, COLOR_WARN),
    ])
    lx = x1 + int(180 * s)
    _text(img, f"Compliant  {int(compliant * 100)}%", (lx, y1 + int(95 * s)), 0.58 * s, COLOR_OK, 2)
    _text(img, f"No Helmet  {int(nh * 100)}%", (lx, y1 + int(128 * s)), 0.58 * s, COLOR_ALERT, 2)
    _text(img, f"No Vest    {int(nv * 100)}%", (lx, y1 + int(161 * s)), 0.58 * s, COLOR_WARN, 2)


def draw_detection_count(img: np.ndarray, stats: Dict) -> None:
    s = _scale(img)
    h, w = img.shape[:2]
    pw, ph = int(310 * s), int(240 * s)
    x2, y2 = w - int(12 * s), h - int(12 * s)
    x1, y1 = x2 - pw, y2 - ph
    _panel(img, x1, y1, x2, y2)
    _text(img, "Detection Count", (x1 + 14, y1 + int(30 * s)), 0.72 * s, COLOR_TEXT, 2)
    rows = [
        ("Workers", stats.get("workers", 0), COLOR_WORKER_BOX),
        ("Forklifts", stats.get("forklifts", 0), COLOR_FORKLIFT),
        ("Road Ways", stats.get("yellow_lines", 0), COLOR_LINE),
        ("No Helmet", stats.get("no_helmet", 0), COLOR_ALERT),
        ("No Vest", stats.get("no_vest", 0), COLOR_WARN),
        ("Boxes", stats.get("boxes", 0), COLOR_BOX),
    ]
    y = y1 + int(64 * s)
    for name, val, color in rows:
        _text(img, name, (x1 + 16, y), 0.60 * s, COLOR_MUTED, 2)
        val_s = str(val)
        (tw, _), _ = cv2.getTextSize(val_s, cv2.FONT_HERSHEY_SIMPLEX, 0.66 * s, 2)
        _text(img, val_s, (x2 - tw - int(16 * s), y), 0.66 * s, color, 2)
        y += int(28 * s)


def draw_yellow_lines(img: np.ndarray, lines: List[Dict]) -> None:
    """Draw aisle ROAD WAY left/right polylines with stable labels."""
    if not lines:
        return

    h, w = img.shape[:2]
    sides = {ln.get('side'): ln for ln in lines if ln.get('side') in ('left', 'right')}
    if 'left' in sides and 'right' in sides:
        left_pts = sides['left'].get('points') or []
        right_pts = sides['right'].get('points') or []
        if len(left_pts) >= 2 and len(right_pts) >= 2:
            poly = np.array(left_pts + list(reversed(right_pts)), dtype=np.int32)
            overlay = img.copy()
            cv2.fillPoly(overlay, [poly], (0, 180, 255))
            cv2.addWeighted(overlay, 0.12, img, 0.88, 0, img)

    for line in lines:
        pts = line.get('points') or []
        if len(pts) < 2:
            continue
        arr = np.array(pts, dtype=np.int32)
        arr = arr[np.argsort(arr[:, 1])]
        cv2.polylines(img, [arr], False, (0, 255, 255), 6, cv2.LINE_AA)
        cv2.polylines(img, [arr], False, COLOR_LINE, 3, cv2.LINE_AA)

        side = line.get('side', 'path')
        if side == 'left':
            label = 'Aisle Road Way (Left)'
        elif side == 'right':
            label = 'Aisle Road Way (Right)'
        else:
            label = 'Yellow Line (Aisle Path)'

        label_tag = line.get('label_tag')
        label_anchor = line.get('label_anchor')
        fs = 0.78
        thick = 2
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
        if label_tag and label_anchor:
            tag_x, tag_y = int(label_tag[0]), int(label_tag[1])
            if len(label_tag) >= 5:
                label = label_tag[4]
            anchor = tuple(map(int, label_anchor))
        else:
            anchor = tuple(map(int, arr[int(len(arr) * 0.55)]))
            if side == 'left':
                tag_x = max(8, int(anchor[0] - tw - 36))
            elif side == 'right':
                tag_x = min(w - tw - 16, int(anchor[0] + 28))
            else:
                tag_x = int(max(0, min(w - tw - 8, anchor[0] - tw // 2)))
            tag_y = int(np.clip(anchor[1], th + 40, int(h * 0.70)))

        # Keep tag on-screen after larger font
        tag_x = int(np.clip(tag_x, 4, max(4, w - tw - 8)))
        tag_y = int(np.clip(tag_y, th + 8, h - 8))
        cv2.line(img, anchor, (tag_x + tw // 2, tag_y - th // 2), COLOR_LINE, 2, cv2.LINE_AA)
        cv2.rectangle(img, (tag_x - 6, tag_y - th - 8), (tag_x + tw + 8, tag_y + 8), COLOR_LINE, -1)
        _text(img, label, (tag_x, tag_y), fs, (10, 10, 10), thick)


def render_dashboard(
    frame: np.ndarray,
    workers: List[Dict],
    forklifts: List[Dict],
    boxes: List[Dict],
    stats: Dict,
    alert: Optional[Dict] = None,
    draw_zones: bool = True,
    yellow_lines: Optional[List[Dict]] = None,
) -> np.ndarray:
    """Compose the full professional safety dashboard onto a frame."""
    img = frame.copy()
    h, w = img.shape[:2]

    yellow_lines = yellow_lines or []

    # Yellow aisle path first (root floor marking)
    draw_yellow_lines(img, yellow_lines)

    # Unsafe / high-risk ONLY next to a real forklift (not fixed shelf markers)
    if draw_zones and forklifts:
        for fl in forklifts:
            draw_unsafe_zone(img, fl["bbox"], "Unsafe Zone - Keep Clear")
            x1, y1, x2, y2 = map(int, fl["bbox"])
            cx = (x1 + x2) // 2
            cy = min(h - 20, y2 + 18)
            draw_high_risk_marker(img, cx, cy, "Forklift Operating Zone")

    # Limit shelf box clutter — only when workers/forklifts present, or few boxes
    show_boxes = boxes
    if not workers and not forklifts:
        show_boxes = []  # empty aisle: don't spam fake "Box" gadgets
    for b in show_boxes[:20]:
        _draw_labeled_box(img, b["bbox"], "Box", COLOR_BOX, 1)

    for fl in forklifts:
        spd = fl.get("speed_kmh")
        over = bool(fl.get("overspeed"))
        if spd is None:
            label = f"Forklift {fl['conf']:.2f}"
            color = COLOR_FORKLIFT
        elif over:
            label = f"OVERSPEED {float(spd):.1f} km/h"
            color = COLOR_ALERT
        else:
            label = f"Forklift {float(spd):.1f} km/h"
            color = COLOR_FORKLIFT
        _draw_labeled_box(img, fl["bbox"], label, color, 3)
        # Speed badge under the box
        if spd is not None:
            x1, y1, x2, y2 = map(int, fl["bbox"])
            lim = float(fl.get("speed_limit_kmh") or stats.get("forklift_speed_limit_kmh") or 8.0)
            badge = f"{float(spd):.1f} / {lim:.0f} km/h"
            bx = x1
            by = min(img.shape[0] - 8, y2 + 32)
            fs, thick = 0.85, 2
            (tw, th), _ = cv2.getTextSize(badge, cv2.FONT_HERSHEY_SIMPLEX, fs, thick)
            cv2.rectangle(img, (bx, by - th - 10), (bx + tw + 16, by + 8), color, -1)
            _text(img, badge, (bx + 8, by), fs, (255, 255, 255), thick)

    for person in workers:
        label = f"Worker {person['conf']:.2f}"
        color = COLOR_WORKER_BOX
        if person.get("no_helmet"):
            label = f"No Helmet {person['conf']:.2f}"
            color = COLOR_ALERT
        elif person.get("no_vest"):
            label = f"No Vest {person['conf']:.2f}"
            color = COLOR_WARN
        _draw_labeled_box(img, person["bbox"], label, color, 2)

    draw_title_bar(img)
    draw_live_summary(img, stats)
    draw_safety_alert(img, alert)
    draw_compliance_pie(img, stats)
    draw_detection_count(img, stats)
    return img
