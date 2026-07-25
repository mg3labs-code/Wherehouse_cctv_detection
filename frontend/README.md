# GLS Safety Dashboard

Production web UI for the GLS Warehouse Safety System.

## Run (dev)

Terminal 1 — API (**port 8001**):
```bash
pip install -r ../requirements.txt
python ../run_api.py
```

Terminal 2 — Frontend:
```bash
npm install
npm run dev
```

Open http://localhost:5173

Vite proxies `/api/*` → `http://127.0.0.1:8001`.

> Port **8000** is often used by `gls-dashboard-production`. Do not point this UI at 8000.

## Pages

- **Safety Analytics** — KPIs, charts, recent violations (from SQLite)
- **Live Monitor** — start/stop YOLO monitor on videos in `data/videos/`, MJPEG stream
- **Reports** — full violation table
- **Inspect Asset** — listed camera/video assets

## Build for production

```bash
cd frontend
npm run build
```

Then serve API (it will mount `frontend/dist` if present):
```bash
python run_api.py
```
Open http://localhost:8001
