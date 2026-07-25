"""Dashboard overlays for Video Project 16 ONLY (Industrial Safety AI style).

Does not affect warehouse aisle / Safe Route / Sawant videos.

Reference look: blue person box, green body point, red danger zone,
WARNING banner, zone absorb time + product touch time.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Match Industrial Safety AI reference (BGR)
COLOR_DANGER = (0, 0, 255)          # red zone / warning
COLOR_PERSON = (255, 120, 40)       # blue person box
COLOR_POINT = (0, 255, 0)           # bright green keypoint
COLOR_SKELETON = (0, 220, 100)
COLOR_TOUCH = (0, 220, 255)
COLOR_OK = (60, 200, 80)
COLOR_WARN = (0, 200, 255)
COLOR_PANEL = (18, 18, 24)
COLOR_BORDER = (70, 70, 80)
COLOR_TEXT = (245, 245, 245)
COLOR_MUTED = (160, 160, 170)

# COCO-17 pose edges
_POSE_EDGES = [
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (5, 11), (6, 12), (11, 12), (11, 13), (13, 15),
    (12, 14), (14, 16), (0, 5), (0, 6),
]


def _panel(img, x1, y1, x2, y2, alpha=0.78):
    ov = img.copy()
    cv2.rectangle(ov, (x1, y1), (x2, y2), COLOR_PANEL, -1)
    cv2.rectangle(ov, (x1, y1), (x2, y2), COLOR_BORDER, 1)
    cv2.addWeighted(ov, alpha, img, 1 - alpha, 0, img)


def _txt(img, text, org, scale=0.55, color=COLOR_TEXT, thick=1):
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def _poly_px(norm_pts: Sequence[Tuple[float, float]], w: int, h: int) -> np.ndarray:
    return np.array([[int(x * w), int(y * h)] for x, y in norm_pts], dtype=np.int32)


def point_in_poly(px: float, py: float, poly: np.ndarray) -> bool:
    return cv2.pointPolygonTest(poly.astype(np.float32), (float(px), float(py)), False) >= 0


def _cover_burned_in_chrome(img: np.ndarray) -> None:
    """Hide clumsy burned-in WARNING strip from the source MP4."""
    h, w = img.shape[:2]
    cv2.rectangle(img, (0, 0), (w, 78), (14, 14, 18), -1)
    fade = np.linspace(1.0, 0.0, 16, dtype=np.float32)
    for i, a in enumerate(fade):
        y = 78 + i
        if y >= h:
            break
        img[y, :] = (img[y, :].astype(np.float32) * (1 - a) + np.array([14, 14, 18]) * a).astype(np.uint8)


def draw_danger_zone(img: np.ndarray, danger_poly: np.ndarray) -> None:
    """Red danger-zone outline (Industrial Safety AI style)."""
    ov = img.copy()
    cv2.fillPoly(ov, [danger_poly], (0, 0, 180))
    cv2.addWeighted(ov, 0.12, img, 0.88, 0, img)
    cv2.polylines(img, [danger_poly], True, COLOR_DANGER, 3, cv2.LINE_AA)
    # Axis-aligned red box around zone (matches reference screenshot)
    x, y, bw, bh = cv2.boundingRect(danger_poly)
    cv2.rectangle(img, (x, y), (x + bw, y + bh), COLOR_DANGER, 2)
    _txt(img, "DANGER ZONE", (x + 8, max(y + 22, 100)), 0.55, COLOR_DANGER, 2)


def draw_warning_banner(img: np.ndarray, text: str) -> None:
    """Top-left WARNING like Industrial Safety AI."""
    h, w = img.shape[:2]
    scale = max(0.75, min(1.15, w / 1400.0))
    thick = 2 if scale < 1.0 else 3
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thick)
    x1, y1 = 10, 82
    x2, y2 = min(w - 10, x1 + tw + 24), y1 + th + 18
    ov = img.copy()
    cv2.rectangle(ov, (x1, y1), (x2, y2), (20, 20, 40), -1)
    cv2.addWeighted(ov, 0.65, img, 0.35, 0, img)
    _txt(img, text, (x1 + 10, y2 - 10), scale, COLOR_DANGER, thick)


def draw_live_alert_panel(img: np.ndarray, info: Dict) -> None:
    h, w = img.shape[:2]
    x1, y1 = 12, int(h * 0.22)
    x2, y2 = int(w * 0.26), int(h * 0.52)
    _panel(img, x1, y1, x2, y2)
    _txt(img, "LIVE ALERT", (x1 + 12, y1 + 24), 0.6, COLOR_DANGER, 2)
    rows = [
        ("Alert Type", info.get("alert_type", "—")),
        ("Object", info.get("object", "—")),
        ("Action", info.get("action", "—")),
        ("Location", info.get("location", "—")),
        ("Risk Level", info.get("risk", "—")),
    ]
    y = y1 + 52
    for k, v in rows:
        _txt(img, k, (x1 + 12, y), 0.42, COLOR_MUTED, 1)
        color = COLOR_DANGER if k == "Risk Level" and str(v).upper() == "HIGH" else COLOR_TEXT
        _txt(img, str(v), (x1 + 12, y + 18), 0.48, color, 1)
        y += 40


def draw_detection_info_panel(img: np.ndarray, info: Dict) -> None:
    h, w = img.shape[:2]
    pw = int(w * 0.26)
    x2, y1 = w - 12, int(h * 0.22)
    x1 = x2 - pw
    y2 = int(h * 0.58)
    _panel(img, x1, y1, x2, y2)
    _txt(img, "DETECTION INFO", (x1 + 12, y1 + 24), 0.55, COLOR_TEXT, 2)
    rows = [
        ("Person Detected", str(info.get("persons", 0))),
        ("Pose Points", str(info.get("pose_points", 0))),
        ("Product Touch", "YES" if info.get("product_touch") else "NO"),
        ("Danger Zone Entry", "YES" if info.get("in_danger") else "NO"),
        ("Zone Absorb Time", info.get("zone_duration", "00:00:00")),
        ("Product Touch Time", info.get("touch_duration", "00:00:00")),
    ]
    y = y1 + 50
    for k, v in rows:
        _txt(img, k, (x1 + 12, y), 0.40, COLOR_MUTED, 1)
        color = COLOR_TEXT
        if v == "YES":
            color = COLOR_DANGER
        elif v == "NO":
            color = COLOR_OK
        elif k.startswith("Person") or k.startswith("Pose"):
            color = COLOR_OK if str(v) != "0" else COLOR_MUTED
        elif "Time" in k and v not in ("00:00:00", "0s", "—"):
            color = COLOR_WARN
        _txt(img, v, (x1 + 12, y + 18), 0.48, color, 1)
        y += 38


def draw_safety_summary(img: np.ndarray, safe_pct: float, warn_pct: float, danger_pct: float, alerts_today: int) -> None:
    h, w = img.shape[:2]
    x1, y2 = 12, h - 12
    y1 = y2 - int(h * 0.18)
    x2 = int(w * 0.30)
    _panel(img, x1, y1, x2, y2)
    _txt(img, "SAFETY SUMMARY", (x1 + 12, y1 + 22), 0.5, COLOR_TEXT, 2)

    cx, cy, r = x1 + 58, (y1 + y2) // 2 + 8, 34
    segs = [(safe_pct, COLOR_OK), (warn_pct, COLOR_WARN), (danger_pct, COLOR_DANGER)]
    start = -90
    for frac, color in segs:
        if frac <= 0:
            continue
        span = max(1, int(360 * frac))
        cv2.ellipse(img, (cx, cy), (r, r), 0, start, start + span, color, -1)
        start += span
    cv2.circle(img, (cx, cy), int(r * 0.48), COLOR_PANEL, -1)

    lx = cx + r + 16
    _txt(img, f"Safe {int(safe_pct * 100)}%", (lx, cy - 14), 0.42, COLOR_OK, 1)
    _txt(img, f"Warning {int(warn_pct * 100)}%", (lx, cy + 4), 0.42, COLOR_WARN, 1)
    _txt(img, f"Danger {int(danger_pct * 100)}%", (lx, cy + 22), 0.42, COLOR_DANGER, 1)
    _txt(img, f"Alerts today: {alerts_today}", (x1 + 12, y2 - 12), 0.42, COLOR_TEXT, 1)


def draw_person_label(img: np.ndarray, person: Dict) -> None:
    """Blue PERSON box + green body point + pose skeleton (reference style)."""
    h, w = img.shape[:2]
    x1, y1, x2, y2 = map(int, person["bbox"])
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w - 1, x2), min(h - 1, y2)
    conf = float(person.get("conf", 0))

    # Blue box like Industrial Safety AI
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 5)
    cv2.rectangle(img, (x1, y1), (x2, y2), COLOR_PERSON, 3)

    label = f"PERSON {conf:.2f}"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
    pad = 8
    lx = int(np.clip(x1, 4, w - tw - 20))
    ly_above = y1 - 10
    if ly_above - th - pad < 100:
        ly = min(y1 + th + pad + 6, y2 - 6)
    else:
        ly = ly_above
    cv2.rectangle(img, (lx, ly - th - pad), (lx + tw + 14, ly + 6), (0, 0, 0), -1)
    cv2.rectangle(img, (lx, ly - th - pad), (lx + tw + 14, ly + 6), COLOR_PERSON, 2)
    _txt(img, label, (lx + 7, ly), 0.65, (255, 255, 255), 2)

    kpts = person.get("keypoints")
    kc = person.get("kp_conf")
    if kpts is not None:
        pts = np.asarray(kpts, dtype=np.float32)
        for a, b in _POSE_EDGES:
            if a >= len(pts) or b >= len(pts):
                continue
            pa, pb = pts[a], pts[b]
            if pa[0] <= 1 or pa[1] <= 1 or pb[0] <= 1 or pb[1] <= 1:
                continue
            if kc is not None and (float(kc[a]) < 0.10 or float(kc[b]) < 0.10):
                continue
            cv2.line(
                img,
                (int(pa[0]), int(pa[1])),
                (int(pb[0]), int(pb[1])),
                COLOR_SKELETON,
                2,
                cv2.LINE_AA,
            )
        for i, p in enumerate(pts):
            if p[0] <= 1 or p[1] <= 1:
                continue
            if kc is not None and float(kc[i]) < 0.10:
                continue
            # Wrists / ankles larger for hand-touch visibility
            r = 7 if i in (9, 10, 15, 16) else 5
            cv2.circle(img, (int(p[0]), int(p[1])), r + 1, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.circle(img, (int(p[0]), int(p[1])), r, COLOR_POINT, -1, cv2.LINE_AA)

    # Primary green absorb/tracking point (torso center) — like reference
    bc = person.get("body_center")
    if bc is not None:
        bx, by = int(bc[0]), int(bc[1])
        cv2.circle(img, (bx, by), 12, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.circle(img, (bx, by), 10, COLOR_POINT, -1, cv2.LINE_AA)
        cv2.circle(img, (bx, by), 3, (255, 255, 255), -1, cv2.LINE_AA)


def draw_product_touch_label(img: np.ndarray, point: Tuple[int, int], touch_duration: str = "") -> None:
    """PRODUCT TOUCH marker + optional duration."""
    x, y = int(point[0]), int(point[1])
    h, w = img.shape[:2]
    x = int(np.clip(x, 8, w - 8))
    y = int(np.clip(y, 8, h - 8))

    cv2.circle(img, (x, y), 32, (0, 0, 0), 5, cv2.LINE_AA)
    cv2.circle(img, (x, y), 32, COLOR_TOUCH, 3, cv2.LINE_AA)
    cv2.circle(img, (x, y), 12, COLOR_TOUCH, -1, cv2.LINE_AA)
    cv2.drawMarker(img, (x, y), (255, 255, 255), cv2.MARKER_CROSS, 16, 2, cv2.LINE_AA)

    label = "PRODUCT TOUCH"
    if touch_duration and touch_duration not in ("00:00:00", "0s"):
        label = f"PRODUCT TOUCH {touch_duration}"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
    lx = int(np.clip(x - tw // 2, int(w * 0.28), w - tw - 24))
    ly = int(np.clip(y + th + 40, th + 100, h - 90))
    cv2.line(img, (x, y), (lx + tw // 2, ly - th), (0, 0, 0), 4, cv2.LINE_AA)
    cv2.line(img, (x, y), (lx + tw // 2, ly - th), COLOR_TOUCH, 2, cv2.LINE_AA)
    cv2.rectangle(img, (lx - 8, ly - th - 8), (lx + tw + 8, ly + 8), (0, 0, 0), -1)
    cv2.rectangle(img, (lx - 8, ly - th - 8), (lx + tw + 8, ly + 8), COLOR_TOUCH, 2)
    _txt(img, label, (lx, ly), 0.65, COLOR_TOUCH, 2)


def render_project16_dashboard(
    frame: np.ndarray,
    people: List[Dict],
    danger_poly: np.ndarray,
    product_poly: np.ndarray,
    in_danger: bool,
    product_touch: bool,
    touch_point: Optional[Tuple[int, int]],
    duration_str: str,
    location: str,
    alerts_today: int,
    touch_duration_str: str = "00:00:00",
    pose_points: int = 0,
) -> np.ndarray:
    """Project-16 Industrial Safety AI UI."""
    img = frame.copy()
    h, w = img.shape[:2]

    _cover_burned_in_chrome(img)

    _txt(img, "Industrial Safety AI - GLS", (12, 28), 0.55, COLOR_TEXT, 1)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    _txt(img, now, (w - 200, 28), 0.45, COLOR_MUTED, 1)
    status = "DANGER" if in_danger else "MONITORING"
    status_color = COLOR_DANGER if in_danger else COLOR_OK
    _txt(img, status, (w // 2 - 60, 28), 0.55, status_color, 2)

    # Red danger zone first (under person overlays)
    draw_danger_zone(img, danger_poly)

    alert_info = {
        "alert_type": (
            "Product Touch Duration" if product_touch and in_danger
            else "Danger Zone Violation" if in_danger
            else "Monitoring"
        ),
        "object": "Person" if people else "—",
        "action": (
            f"Touch {touch_duration_str}" if product_touch
            else ("Zone Absorb" if in_danger else "Clear")
        ),
        "location": location,
        "risk": "HIGH" if in_danger or product_touch else "LOW",
    }
    det_info = {
        "persons": len(people),
        "pose_points": pose_points,
        "product_touch": product_touch,
        "in_danger": in_danger,
        "zone_duration": duration_str,
        "touch_duration": touch_duration_str,
    }
    draw_live_alert_panel(img, alert_info)
    draw_detection_info_panel(img, det_info)

    if in_danger and product_touch:
        safe, warn, danger = 0.55, 0.15, 0.30
    elif in_danger:
        safe, warn, danger = 0.70, 0.15, 0.15
    else:
        safe, warn, danger = 0.90, 0.08, 0.02
    draw_safety_summary(img, safe, warn, danger, alerts_today)

    for p in people:
        draw_person_label(img, p)

    if product_touch and touch_point:
        draw_product_touch_label(img, touch_point, touch_duration_str)

    if in_danger:
        if product_touch:
            draw_warning_banner(img, "WARNING : PERSON TOUCHING PRODUCT")
        else:
            draw_warning_banner(img, "WARNING : PERSON IN DANGER ZONE")

    return img
