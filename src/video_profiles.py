"""Per-video monitoring profiles.

Only matched videos get special labels/zones. Everything else uses the
default warehouse aisle profile unchanged.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional


# Default = existing GLS warehouse aisle monitor (forklift / PPE / road ways)
DEFAULT_PROFILE = "warehouse_aisle"

# Video Project 16 — production-line danger / product-touch UI only
VIDEO_PROJECT_16 = "video_project_16"

# GODOWN NO-3 box aisle — Safe Route + PPE (No Helmet) UI only
SAFE_ROUTE_NO3 = "safe_route_no3"

# Sawant / open-floor forklift demo — no aisle lines; detect yellow forklift + PPE
SAWANT_FORKLIFT = "sawant_forklift"

PROFILES: Dict[str, Dict[str, Any]] = {
    DEFAULT_PROFILE: {
        "name": "warehouse_aisle",
        "title": "GLS Warehouse Safety Monitor - AI Powered",
        "enable_yellow_lines": True,
        "enable_forklift_lights": True,
        "enable_ppe_dashboard": True,
        "mode": "warehouse",
    },
    SAWANT_FORKLIFT: {
        "name": SAWANT_FORKLIFT,
        "title": "GLS Warehouse Safety Monitor - AI Powered",
        "mode": "sawant_forklift",
        "location": "Forklift Operations",
        # This clip has no painted aisle road-ways — hide Left/Right lines
        "enable_yellow_lines": False,
        "enable_forklift_lights": False,
        "enable_ppe_dashboard": True,
        # COCO often labels the yellow forklift as truck/bus on this video
        "map_coco_vehicles": True,
        "detect_yellow_forklift": True,
        "forklift_max_width_frac": 1.0,
        "forklift_max_area_frac": 0.95,
        "forklift_aisle_x_min": 0.0,
        "forklift_aisle_x_max": 1.0,
        "forklift_vehicle_min_conf": 0.15,
        # Close-up demo: keep tracks across slow AI samples; measure speed in video-time
        "forklift_track_max_dist": 320,
        "forklift_track_ttl": 20.0,
        "forklift_ref_height_m": 2.0,
    },
    VIDEO_PROJECT_16: {
        "name": VIDEO_PROJECT_16,
        "title": "Industrial Safety AI - GLS",
        "mode": "project16",
        "location": "Production Line - Zone B",
        # Fire PRODUCT TOUCH on first confirmed contact (seconds for duration alert)
        "touch_alert_seconds": 1.0,
        # 1 = alert the moment hand lands on product (live AI is already sparse)
        "touch_confirm_frames": 1,
        # Max px from wrist/fingertip to fiber pile edge still counts as contact
        "touch_snap_px": 20,
        # Machine / working pit (person standing on platform counts as in-zone)
        "danger_zone": [
            (0.15, 0.10),
            (0.92, 0.10),
            (0.95, 0.88),
            (0.12, 0.90),
        ],
        # Hopper / fiber pile (hands reach here — not walkway)
        "product_zone": [
            (0.22, 0.24),
            (0.70, 0.20),
            (0.74, 0.60),
            (0.24, 0.66),
        ],
    },
    SAFE_ROUTE_NO3: {
        "name": SAFE_ROUTE_NO3,
        "title": "GLS Warehouse Safety Monitor - AI Powered",
        "mode": "safe_route",
        "location": "Zone B - Aisle 4",
        # No forklift light FPs on cardboard-box aisles
        "enable_forklift_lights": False,
        "enable_yellow_lines": True,
        "route_label": "Safe Route",
    },
}

# Filename matchers (case-insensitive substring of basename without extension)
# Order matters: more specific first.
_PROFILE_MATCHERS = (
    ("video project 16", VIDEO_PROJECT_16),
    ("videoproject16", VIDEO_PROJECT_16),
    # Cardboard-box Safe Route scene — GODOWN NO-3 only (not GODOWN-1 / 2A / Project 16)
    ("godown no-3", SAFE_ROUTE_NO3),
    ("godown no 3", SAFE_ROUTE_NO3),
    ("godown_no-3", SAFE_ROUTE_NO3),
    ("godown_no_3", SAFE_ROUTE_NO3),
    # Open-floor forklift demo (Sawant) — no aisle road-way overlays
    ("sawant", SAWANT_FORKLIFT),
    ("wear house working with forklift", SAWANT_FORKLIFT),
    ("warehouse working with forklift", SAWANT_FORKLIFT),
    ("sawantforkliftservices", SAWANT_FORKLIFT),
)


def resolve_profile(source: Any) -> Dict[str, Any]:
    """Return profile dict for a video path / camera index. Others → warehouse."""
    if source is None or isinstance(source, int):
        return dict(PROFILES[DEFAULT_PROFILE])

    path = str(source)
    stem = os.path.splitext(os.path.basename(path))[0].lower().strip()
    stem_compact = stem.replace(" ", "").replace("_", "").replace("-", "")

    for needle, key in _PROFILE_MATCHERS:
        needle_c = needle.replace(" ", "").replace("-", "").replace("_", "")
        if needle in stem or needle_c in stem_compact:
            return dict(PROFILES[key])

    return dict(PROFILES[DEFAULT_PROFILE])


def is_project16(profile: Optional[Dict[str, Any]]) -> bool:
    return bool(profile) and profile.get("mode") == "project16"


def is_safe_route(profile: Optional[Dict[str, Any]]) -> bool:
    return bool(profile) and profile.get("mode") == "safe_route"


def is_sawant_forklift(profile: Optional[Dict[str, Any]]) -> bool:
    return bool(profile) and profile.get("mode") == "sawant_forklift"
