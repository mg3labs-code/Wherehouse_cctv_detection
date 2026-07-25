import { useEffect, useRef, useState } from 'react'
import { resolveApiOrigin, api, type LiveStatus, type VideoItem } from '../api/client'

export function LiveMonitorPage() {
  const [videos, setVideos] = useState<VideoItem[]>([])
  const [selected, setSelected] = useState('')
  const [status, setStatus] = useState<LiveStatus | null>(null)
  const [frameUrl, setFrameUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const tickRef = useRef(0)

  function refreshFrame() {
    // Poll single JPEGs — Chrome often shows a black box for MJPEG <img>
    const origin = resolveApiOrigin()
    tickRef.current += 1
    setFrameUrl(`${origin}/api/live/frame.jpg?t=${Date.now()}_${tickRef.current}`)
  }

  async function refreshStatus() {
    try {
      const s = await api.liveStatus()
      setStatus(s)
      if (s.status === 'api-offline') {
        setError('API offline — run python run_api.py on port 8001')
      } else {
        setError((prev) =>
          prev && (prev.startsWith('API offline') || prev.includes('is API on'))
            ? null
            : prev,
        )
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Status failed')
    }
  }

  useEffect(() => {
    let cancelled = false
    api.videos()
      .then((r) => {
        if (cancelled) return
        const items = Array.isArray(r.items) ? r.items : []
        setVideos(items)
        if (items.length) setSelected(items[0].path)
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Videos failed — is API on :8001?')
      })
    refreshStatus()
    refreshFrame()
    const statusId = setInterval(refreshStatus, 2000)
    // ~20 FPS poll so 1× backend playback looks smooth (was 250ms = 4 FPS)
    const frameId = setInterval(refreshFrame, 50)
    return () => {
      cancelled = true
      clearInterval(statusId)
      clearInterval(frameId)
    }
  }, [])

  async function start() {
    if (!selected) return
    setBusy(true)
    setError(null)
    try {
      const s = await api.liveStart(selected)
      setStatus(s)
      refreshFrame()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Start failed')
    } finally {
      setBusy(false)
    }
  }

  async function stop() {
    setBusy(true)
    try {
      const s = await api.liveStop()
      setStatus(s)
      refreshFrame()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Stop failed')
    } finally {
      setBusy(false)
    }
  }

  const online = status?.running

  return (
    <>
      <div className="breadcrumb">Home &gt; <strong>Live Monitor</strong></div>
      <div className="tabs">
        <button className="tab active">Live Camera Feed</button>
        <span className={`online-pill ${online ? '' : 'offline'}`}>
          <span className="dot" />
          {status?.status || 'idle'}
        </span>
      </div>

      <div className="filters">
        <div className="filter-field" style={{ minWidth: 320, flex: 1 }}>
          <label>Video Source</label>
          <select value={selected} onChange={(e) => setSelected(e.target.value)}>
            {videos.map((v) => (
              <option key={v.path} value={v.path}>
                {v.id}. {v.name} ({v.size_mb} MB)
              </option>
            ))}
          </select>
        </div>
        <button className="btn btn-primary" disabled={busy || !selected} onClick={start}>
          {busy ? 'Starting…' : 'Start Monitor'}
        </button>
        <button className="btn btn-danger" disabled={busy || !online} onClick={stop}>
          Stop
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {status?.status === 'error' && status.last_alert && (
        <p className="error">
          Monitor error: {status.last_alert}
          {status.last_alert.includes('Application Control') || status.last_alert.includes('_regex') ? (
            <>
              {' '}
              Windows blocked a Python DLL. Allow it in Windows Security, or recreate the venv with Python 3.11.
            </>
          ) : null}
        </p>
      )}
      {status?.status === 'starting' && <p className="muted">Loading YOLO model… this can take ~15s.</p>}

      <div className="live-layout">
        <div className="live-frame">
          {frameUrl ? (
            <img src={frameUrl} alt="Live annotated feed" />
          ) : (
            <p className="muted">Connecting to live feed…</p>
          )}
        </div>
        <div className="card">
          <h3>Detection Status</h3>
          <table className="data">
            <tbody>
              <tr><td>Profile</td><td><strong>{status?.profile || '—'}</strong></td></tr>
              <tr><td>FPS</td><td>{status?.fps ?? 0}</td></tr>
              <tr><td>Frame</td><td>{status?.frame ?? 0}</td></tr>
              <tr><td>Workers</td><td>{status?.workers ?? 0}</td></tr>
              <tr><td>Forklifts</td><td>{status?.forklifts ?? 0}</td></tr>
              <tr>
                <td>Forklift Speed</td>
                <td>
                  {status?.forklifts ? (
                    <strong style={{ color: status.forklift_overspeed ? '#dc2626' : undefined }}>
                      {(status.forklift_speed_kmh ?? 0).toFixed(1)} km/h
                      {status.forklift_overspeed ? ' ⚠ OVERSPEED' : ''}
                      <span className="muted"> / limit {(status.forklift_speed_limit_kmh ?? 8).toFixed(0)} km/h</span>
                    </strong>
                  ) : (
                    '—'
                  )}
                </td>
              </tr>
              <tr><td>Road Ways / Safe Route</td><td>{status?.road_ways ?? 0}{status?.aisle_locked ? ' (locked)' : ''}</td></tr>
              <tr><td>Session Violations</td><td>{status?.violations_session ?? 0}</td></tr>
              <tr><td>Last Alert</td><td>{status?.last_alert || 'None'}</td></tr>
              <tr><td>Source</td><td className="muted">{status?.source || '—'}</td></tr>
            </tbody>
          </table>
          <p className="muted" style={{ marginTop: 14 }}>
            Live stream uses the same YOLO labels as <code>python run_video.py</code>.
            Wait until status is <strong>online</strong> (aisle / safe-route lines lock) before judging labels.
          </p>
        </div>
      </div>
    </>
  )
}
