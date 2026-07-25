"""Dashboard for GODOWN NO-3 Safe Route + PPE mode ONLY.

Matches the Safe Route / No Helmet reference UI. Does not affect other videos.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import cv2
import numpy as np

from .dashboard import (
    COLOR_ALERT,
    COLOR_LINE,
    COLOR_MUTED,
    COLOR_OK,
    COLOR_TEXT,
    COLOR_WARN,
    COLOR_WORKER_BOX,
    _draw_labeled_box,
    _draw_pie,
    _panel,
    _scale,
    _text,
    draw_title_bar,
)


def _draw_safe_route(img: np.ndarray, lines: List[Dict]) -> None:
    """Safe Route edges + dashed center guide with fixed Left/Right labels.

    When lines are locked (`label_tag` / `locked`), geometry and tags never
    recompute — same behavior as Aisle Road Way.
    """
    if not lines:
        return

    h, w = img.shape[:2]
    sides = {ln.get("side"): ln for ln in lines if ln.get("side") in ("left", "right")}
    locked = all(bool((sides.get(s) or {}).get("locked") or (sides.get(s) or {}).get("label_tag"))
                 for s in ("left", "right") if s in sides)

    left_pts = list((sides.get("left") or {}).get("points") or [])
    right_pts = list((sides.get("right") or {}).get("points") or [])

    # Only synthesize a missing edge while unlocking — never after freeze
    if not locked:
        if len(left_pts) >= 2 and len(right_pts) < 2:
            right_pts = [(min(w - 2, int(x + w * 0.22)), y) for x, y in left_pts]
        elif len(right_pts) >= 2 and len(left_pts) < 2:
            left_pts = [(max(2, int(x - w * 0.22)), y) for x, y in right_pts]

    if len(left_pts) >= 2 and len(right_pts) >= 2:
        poly = np.array(left_pts + list(reversed(right_pts)), dtype=np.int32)
        ov = img.copy()
        cv2.fillPoly(ov, [poly], (0, 200, 255))
        cv2.addWeighted(ov, 0.12, img, 0.88, 0, img)

        n = min(len(left_pts), len(right_pts))
        center = []
        for i in range(n):
            lx, ly = left_pts[i]
            rx, ry = right_pts[min(i, len(right_pts) - 1)]
            center.append((int((lx + rx) / 2), int((ly + ry) / 2)))
        center = sorted(center, key=lambda p: p[1], reverse=True)

        for i in range(0, len(center) - 1, 2):
            p1, p2 = center[i], center[i + 1]
            cv2.line(img, p1, p2, (0, 255, 255), 2, cv2.LINE_AA)
            if i % 4 == 0:
                cv2.arrowedLine(img, p1, p2, COLOR_LINE, 2, tipLength=0.4)

    # Draw ONLY real locked/detected sides (no synthetic label jitter)
    for side in ("left", "right"):
        real = sides.get(side)
        if not real:
            continue
        pts = list(real.get("points") or [])
        if len(pts) < 2:
            continue
        arr = np.array(pts, dtype=np.int32)
        arr = arr[np.argsort(arr[:, 1])]
        cv2.polylines(img, [arr], False, (0, 255, 255), 7, cv2.LINE_AA)
        cv2.polylines(img, [arr], False, COLOR_LINE, 4, cv2.LINE_AA)

        label_tag = real.get("label_tag")
        label_anchor = real.get("label_anchor")
        if label_tag and label_anchor:
            # Frozen — pixel-exact, never recalculate
            tag_x, tag_y, tw, th, label = label_tag
            anchor = (int(label_anchor[0]), int(label_anchor[1]))
            tag_x, tag_y, tw, th = int(tag_x), int(tag_y), int(tw), int(th)
        else:
            # Acquisition only (brief). Prefer freeze ASAP in monitor.
            anchor = (int(arr[int(len(arr) * 0.55)][0]), int(arr[int(len(arr) * 0.55)][1]))
            label = f"Safe Route ({side.capitalize()})"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            if side == "left":
                tag_x = max(8, int(anchor[0] - tw - 36))
            else:
                tag_x = min(w - tw - 16, int(anchor[0] + 28))
            tag_y = int(np.clip(anchor[1], th + 40, int(h * 0.70)))

        # Same callout style as Aisle Road Way (Left/Right)
        cv2.line(img, anchor, (tag_x + tw // 2, tag_y - th // 2), COLOR_LINE, 2, cv2.LINE_AA)
        cv2.rectangle(img, (tag_x - 4, tag_y - th - 4), (tag_x + tw + 4, tag_y + 4), COLOR_LINE, -1)
        _text(img, label, (tag_x, tag_y), 0.5, (10, 10, 10), 1)


def _draw_live_summary(img: np.ndarray, stats: Dict) -> None:
    s = _scale(img)
    x1, y1 = int(12 * s), int(52 * s)
    x2, y2 = int(310 * s), int(300 * s)
    _panel(img, x1, y1, x2, y2)
    _text(img, "Live Safety Summary", (x1 + 12, y1 + int(24 * s)), 0.62 * s, COLOR_TEXT, 2)
    rows = [
        ("Total Detections", stats.get("total", 0), COLOR_TEXT),
        ("Workers Detected", stats.get("workers", 0), COLOR_WORKER_BOX),
        ("No Helmet", stats.get("no_helmet", 0), COLOR_ALERT if stats.get("no_helmet") else COLOR_OK),
        ("No Vest", stats.get("no_vest", 0), COLOR_WARN if stats.get("no_vest") else COLOR_OK),
        ("Forklifts", 0, COLOR_MUTED),
        ("Unsafe Zones", stats.get("unsafe_zones", 0), COLOR_ALERT if stats.get("unsafe_zones") else COLOR_OK),
        ("PPE Compliance", f"{stats.get('ppe_pct', 100)}%", COLOR_OK if stats.get("ppe_pct", 100) >= 80 else COLOR_WARN),
    ]
    y = y1 + int(52 * s)
    for name, val, color in rows:
        _text(img, name, (x1 + 14, y), 0.48 * s, COLOR_MUTED, 1)
        _text(img, str(val), (x1 + 170, y), 0.52 * s, color, 2)
        y += int(30 * s)


def _draw_compliance_pie(img: np.ndarray, stats: Dict) -> None:
    """Compliant / Warning / Violation donut like the reference mockup."""
    s = _scale(img)
    h = img.shape[0]
    x1 = int(12 * s)
    y2 = h - int(150 * s)
    y1 = y2 - int(150 * s)
    x2 = int(310 * s)
    _panel(img, x1, y1, x2, y2)
    _text(img, "Safety Compliance", (x1 + 12, y1 + int(22 * s)), 0.55 * s, COLOR_TEXT, 2)

    ppe = float(stats.get("ppe_pct", 100))
    no_h = 1 if stats.get("no_helmet") else 0
    no_v = 1 if stats.get("no_vest") else 0
    if stats.get("workers", 0) == 0:
        segs = [(1.0, COLOR_OK)]
        labels = [("Compliant 100%", COLOR_OK)]
    else:
        viol = 0.25 if no_h else 0.0
        warn = 0.25 if (no_v or (no_h and ppe >= 40)) else (0.15 if ppe < 80 else 0.0)
        safe = max(0.0, 1.0 - viol - warn)
        if no_h and not no_v:
            segs = [(0.50, COLOR_OK), (0.25, COLOR_WARN), (0.25, COLOR_ALERT)]
            labels = [
                ("Compliant 50%", COLOR_OK),
                ("Warning 25%", COLOR_WARN),
                ("Violation 25%", COLOR_ALERT),
            ]
        elif no_h and no_v:
            segs = [(0.0, COLOR_OK), (0.5, COLOR_WARN), (0.5, COLOR_ALERT)]
            labels = [("No Helmet 50%", COLOR_ALERT), ("No Vest 50%", COLOR_WARN)]
        else:
            segs = [(safe, COLOR_OK), (warn, COLOR_WARN), (viol, COLOR_ALERT)]
            labels = [
                (f"Compliant {int(safe * 100)}%", COLOR_OK),
                (f"Warning {int(warn * 100)}%", COLOR_WARN),
                (f"Violation {int(viol * 100)}%", COLOR_ALERT),
            ]

    cx = x1 + int(70 * s)
    cy = (y1 + y2) // 2 + int(8 * s)
    _draw_pie(img, cx, cy, int(42 * s), [(max(0.01, a), c) for a, c in segs if a > 0])
    ly = y1 + int(50 * s)
    for text, color in labels:
        _text(img, text, (x1 + int(130 * s), ly), 0.42 * s, color, 1)
        ly += int(22 * s)


def _draw_alert(img: np.ndarray, alert: Optional[Dict]) -> None:
    if not alert:
        return
    s = _scale(img)
    w = img.shape[1]
    pw = int(340 * s)
    x2, y1 = w - int(12 * s), int(52 * s)
    x1 = x2 - pw
    y2 = y1 + int(140 * s)
    ov = img.copy()
    cv2.rectangle(ov, (x1, y1), (x2, y2), (35, 35, 210), -1)
    cv2.addWeighted(ov, 0.82, img, 0.18, 0, img)
    cv2.rectangle(img, (x1, y1), (x2, y2), (80, 80, 255), 2)
    _text(img, "SAFETY ALERT", (x1 + 16, y1 + int(30 * s)), 0.72 * s, (255, 255, 255), 2)
    _text(img, str(alert.get("title", "")), (x1 + 16, y1 + int(62 * s)), 0.58 * s, (255, 255, 255), 2)
    _text(img, f"Location: {alert.get('location', '')}", (x1 + 16, y1 + int(94 * s)), 0.46 * s, (235, 235, 255), 1)
    _text(img, f"Time: {alert.get('time', '')}", (x1 + 16, y1 + int(118 * s)), 0.46 * s, (235, 235, 255), 1)


def _draw_route_analytics(img: np.ndarray, stats: Dict) -> None:
    s = _scale(img)
    h = img.shape[0]
    x1, y2 = int(12 * s), h - int(12 * s)
    y1 = y2 - int(128 * s)
    x2 = int(310 * s)
    _panel(img, x1, y1, x2, y2)
    _text(img, "Route Analytics", (x1 + 12, y1 + int(22 * s)), 0.55 * s, COLOR_TEXT, 2)
    rows = [
        ("Route Status", "Safe" if stats.get("route_ok") else "—"),
        ("Route Path", stats.get("route_path", "—")),
        ("Distance Covered", f"{stats.get('distance_m', 0):.1f} m"),
        ("Est. Time to End", stats.get("eta", "—")),
    ]
    y = y1 + int(48 * s)
    for k, v in rows:
        _text(img, k, (x1 + 12, y), 0.42 * s, COLOR_MUTED, 1)
        color = COLOR_OK if k == "Route Status" and v == "Safe" else COLOR_TEXT
        _text(img, str(v), (x1 + 150, y), 0.45 * s, color, 1)
        y += int(20 * s)


def _draw_detection_count(img: np.ndarray, stats: Dict) -> None:
    s = _scale(img)
    h, w = img.shape[:2]
    pw = int(230 * s)
    x2, y2 = w - int(12 * s), h - int(12 * s)
    x1 = x2 - pw
    y1 = y2 - int(175 * s)
    _panel(img, x1, y1, x2, y2)
    _text(img, "Detection Count", (x1 + 12, y1 + int(22 * s)), 0.52 * s, COLOR_TEXT, 2)
    rows = [
        ("Workers", stats.get("workers", 0), COLOR_WORKER_BOX),
        ("No Helmet", stats.get("no_helmet", 0), COLOR_ALERT if stats.get("no_helmet") else COLOR_OK),
        ("No Vest", stats.get("no_vest", 0), COLOR_WARN if stats.get("no_vest") else COLOR_OK),
        ("Forklifts", 0, COLOR_MUTED),
        ("Unsafe Zones", stats.get("unsafe_zones", 0), COLOR_ALERT if stats.get("unsafe_zones") else COLOR_OK),
        ("Boxes", stats.get("boxes", 0), COLOR_OK),
    ]
    y = y1 + int(48 * s)
    for name, val, color in rows:
        _text(img, name, (x1 + 12, y), 0.42 * s, COLOR_MUTED, 1)
        _text(img, str(val), (x1 + 145, y), 0.48 * s, color, 2)
        y += int(18 * s)


def _draw_safe_banner(img: np.ndarray, route_ok: bool) -> None:
    if not route_ok:
        return
    h, w = img.shape[:2]
    msg = "SAFE ROUTE ACTIVE  —  Please follow the marked route for safe movement."
    bw = min(w - 48, 820)
    bx1 = (w - bw) // 2
    by2 = h - int(h * 0.02) - 8
    by1 = by2 - 40
    ov = img.copy()
    cv2.rectangle(ov, (bx1, by1), (bx1 + bw, by2), (35, 150, 70), -1)
    cv2.addWeighted(ov, 0.78, img, 0.22, 0, img)
    cv2.rectangle(img, (bx1, by1), (bx1 + bw, by2), (80, 220, 120), 2)
    # shield mark
    cx, cy = bx1 + 28, (by1 + by2) // 2
    cv2.circle(img, (cx, cy), 12, (255, 255, 255), 2)
    cv2.putText(img, "OK", (cx - 10, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
    _text(img, msg, (bx1 + 50, by1 + 26), 0.52, (255, 255, 255), 1)


def render_safe_route_dashboard(
    frame: np.ndarray,
    workers: List[Dict],
    boxes: List[Dict],
    yellow_lines: List[Dict],
    stats: Dict,
    alert: Optional[Dict] = None,
) -> np.ndarray:
    """Compose second-pic Safe Route + PPE dashboard (GODOWN NO-3 only)."""
    img = frame.copy()
    h, w = img.shape[:2]

    _draw_safe_route(img, yellow_lines or [])

    # Only a couple of box labels when workers present (avoid shelf spam)
    for b in (boxes or [])[:2]:
        _draw_labeled_box(img, b["bbox"], "Box", (80, 220, 80), 1)

    for person in workers:
        conf = float(person.get("conf", 0))
        if person.get("no_helmet"):
            label, color = f"No Helmet {conf:.2f}", COLOR_ALERT
        elif person.get("no_vest"):
            label, color = f"No Vest {conf:.2f}", COLOR_WARN
        else:
            label, color = f"Worker {conf:.2f}", COLOR_WORKER_BOX
        _draw_labeled_box(img, person["bbox"], label, color, 2)

    draw_title_bar(img)
    # LIVE + stream meta (second pic)
    cv2.circle(img, (w - 200, 22), 7, (40, 40, 230), -1)
    _text(img, "LIVE", (w - 186, 28), 0.5, (255, 255, 255), 1)
    _text(img, "FILE - MJPEG", (w - 360, 28), 0.4, (200, 200, 200), 1)
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    _text(img, ts, (w - 560, 28), 0.45, COLOR_TEXT, 1)

    _draw_live_summary(img, stats)
    _draw_alert(img, alert)
    _draw_compliance_pie(img, stats)
    _draw_route_analytics(img, stats)
    _draw_detection_count(img, stats)
    _draw_safe_banner(img, bool(stats.get("route_ok")))

    return img
