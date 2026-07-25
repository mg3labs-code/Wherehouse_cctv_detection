"""GLS Warehouse Safety — FastAPI backend."""
from __future__ import annotations

import glob
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..config import Config
from . import store
from .live import live_service

app = FastAPI(
    title="GLS Warehouse Safety API",
    version="1.0.0",
    description="Production API for GLS warehouse safety analytics and live monitoring",
)

app.add_middleware(
    CORSMiddleware,
    # Dev UI on :5173 + prod same-origin; allow stream/img from Vite
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartLiveBody(BaseModel):
    source: str


@app.on_event("startup")
def on_startup():
    store.init_db()
    # Real-time only — drop any old demo seed rows
    store.purge_demo_events()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "gls-warehouse-safety",
        "live": live_service.status().get("status"),
    }


@app.get("/api/worksites")
def get_worksites():
    return {"worksites": store.worksites()}


@app.get("/api/analytics/summary")
def analytics_summary(worksite: Optional[str] = Query(None)):
    ws = None if not worksite or worksite in ("all", "--All Worksites--") else worksite
    return store.summary_kpis(ws)


@app.get("/api/analytics/timeseries")
def analytics_timeseries(
    days: int = Query(14, ge=7, le=90),
    worksite: Optional[str] = Query(None),
):
    ws = None if not worksite or worksite in ("all", "--All Worksites--") else worksite
    return {"series": store.timeseries(days=days, worksite=ws)}


@app.get("/api/violations")
def get_violations(
    limit: int = Query(50, ge=1, le=500),
    worksite: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
):
    ws = None if not worksite or worksite in ("all", "--All Worksites--") else worksite
    return {"items": store.list_events(limit=limit, worksite=ws, event_type=event_type)}


@app.get("/api/videos")
def list_videos():
    video_dir = os.path.join(Config.DATA_DIR, "videos")
    os.makedirs(video_dir, exist_ok=True)
    files = []
    for ext in ("*.mp4", "*.MP4", "*.avi", "*.mkv", "*.mov"):
        files.extend(glob.glob(os.path.join(video_dir, ext)))
    files = sorted(set(files))
    items = []
    for i, path in enumerate(files, 1):
        items.append({
            "id": i,
            "name": os.path.basename(path),
            "path": os.path.relpath(path, Config.PROJECT_ROOT).replace("\\", "/"),
            "size_mb": round(os.path.getsize(path) / (1024 * 1024), 1),
        })
    return {"items": items}


@app.get("/api/live/status")
def live_status():
    return live_service.status()


@app.post("/api/live/start")
def live_start(body: StartLiveBody):
    try:
        return live_service.start(body.source)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live/stop")
def live_stop():
    return live_service.stop()


@app.get("/api/live/frame.jpg")
def live_frame():
    """Single latest JPEG — reliable for browsers that break on MJPEG."""
    import numpy as np
    import cv2

    jpeg = live_service.latest_jpeg()
    if not jpeg:
        blank = np.zeros((360, 640, 3), dtype=np.uint8)
        cv2.putText(
            blank, "Waiting for live feed...", (80, 180),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2,
        )
        ok, buf = cv2.imencode(".jpg", blank)
        jpeg = buf.tobytes() if ok else b""
    return Response(
        content=jpeg,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        },
    )


@app.get("/api/live/stream")
def live_stream():
    """MJPEG multipart stream of annotated frames."""

    def gen():
        import time
        last = None
        while True:
            jpeg = live_service.latest_jpeg()
            if not jpeg:
                import numpy as np
                import cv2
                blank = np.zeros((360, 640, 3), dtype=np.uint8)
                cv2.putText(
                    blank, "Waiting for live feed...", (80, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2,
                )
                ok, buf = cv2.imencode(".jpg", blank)
                jpeg = buf.tobytes() if ok else None
            if jpeg and jpeg is not last:
                last = jpeg
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(jpeg)).encode() + b"\r\n"
                    b"\r\n" + jpeg + b"\r\n"
                )
            time.sleep(0.08)

    return StreamingResponse(
        gen(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-cache, no-store", "Connection": "close"},
    )


# Optional: serve built frontend from frontend/dist when present
_DIST = os.path.join(Config.PROJECT_ROOT, "frontend", "dist")
if os.path.isdir(_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="assets")

    @app.get("/")
    def spa_index():
        return FileResponse(os.path.join(_DIST, "index.html"))

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not found")
        index = os.path.join(_DIST, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Frontend not built")
