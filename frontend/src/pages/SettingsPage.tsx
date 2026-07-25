export function SettingsPage() {
  return (
    <>
      <div className="breadcrumb">Home &gt; <strong>Settings</strong></div>
      <div className="card">
        <h3>System Settings</h3>
        <p className="muted">
          Dev: Vite proxies JSON <code>/api</code> → <code>http://127.0.0.1:8001</code>.
          Live MJPEG streams directly from port <strong>8001</strong>.
          Model: YOLO26. Profiles: warehouse aisle, Safe Route (NO-3), Video Project 16.
        </p>
        <ul className="muted">
          <li>Backend: <code>python run_api.py</code> → FastAPI :8001 + SQLite</li>
          <li>Frontend: <code>npm run dev</code> → React :5173</li>
          <li>Live: MJPEG from ComplianceMonitor</li>
        </ul>
      </div>
    </>
  )
}
