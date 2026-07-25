/**
 * Frontend ↔ backend client.
 *
 * Dev: Vite proxies `/api/*` JSON to :8001. MJPEG stream hits :8001 directly
 * (avoids Vite proxy buffering that freezes the live feed).
 * Prod: same origin when served from FastAPI on :8001.
 */

export type Summary = {
  safety_score: number
  safety_label: string
  incidents_prevented: number
  asset_hours: number
  assets: number
  operators: number
  total_alerts: number
  high_severity: number
  medium_severity: number
  by_type: Record<string, number>
  online: boolean
}

export type SeriesPoint = {
  date: string
  incidents: number
  overrides: number
  emergency: number
}

export type Violation = {
  id: number
  ts: string
  source: string
  profile: string
  event_type: string
  severity: string
  worksite: string
  payload: Record<string, unknown>
}

export type VideoItem = {
  id: number
  name: string
  path: string
  size_mb: number
}

export type LiveStatus = {
  running: boolean
  source: string | null
  profile: string | null
  fps: number
  frame: number
  workers: number
  forklifts: number
  forklift_speed_kmh: number
  forklift_speed_limit_kmh: number
  forklift_overspeed: boolean
  road_ways: number
  violations_session: number
  last_alert: string | null
  status: string
  aisle_locked: boolean
}

/**
 * Backend origin for MJPEG stream.
 * - Localhost: hit :8001 directly (avoids Vite buffering)
 * - ngrok / remote: same-origin `/api` via Vite proxy (127.0.0.1 is unreachable from outside)
 * - Override anytime with VITE_API_ORIGIN
 */
export function resolveApiOrigin(): string {
  const env = (import.meta.env.VITE_API_ORIGIN as string | undefined)?.replace(/\/$/, '')
  if (env) return env
  if (!import.meta.env.DEV) return ''
  if (typeof window === 'undefined') return 'http://127.0.0.1:8001'
  const host = window.location.hostname
  const local = host === 'localhost' || host === '127.0.0.1' || host === '[::1]'
  return local ? 'http://127.0.0.1:8001' : ''
}

export const API_ORIGIN: string = resolveApiOrigin()

function apiPath(path: string): string {
  // JSON calls stay relative so Vite proxy works and cookies aren't needed
  return path.startsWith('/') ? path : `/${path}`
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(apiPath(path))
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(apiPath(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(detail || `${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

function normalizeVideos(raw: unknown): VideoItem[] {
  if (!raw || typeof raw !== 'object') return []
  const obj = raw as Record<string, unknown>
  if (Array.isArray(obj.items)) {
    return obj.items as VideoItem[]
  }
  // Compat with gls-dashboard-production shape { files: [{name,path,size}] }
  if (Array.isArray(obj.files)) {
    return (obj.files as Array<Record<string, unknown>>).map((f, i) => ({
      id: i + 1,
      name: String(f.name || ''),
      path: String(f.path || f.name || ''),
      size_mb: typeof f.size === 'number' ? Math.round(((f.size as number) / 1048576) * 10) / 10 : 0,
    }))
  }
  return []
}

export const api = {
  /** True when FastAPI /api/health responds OK. */
  async ping(): Promise<boolean> {
    try {
      const h = await get<{ status?: string }>('/api/health')
      return h?.status === 'ok'
    } catch {
      return false
    }
  },

  health: () => get<Record<string, unknown>>('/api/health'),
  worksites: () => get<{ worksites: string[] }>('/api/worksites'),
  summary: (worksite?: string) =>
    get<Summary>(`/api/analytics/summary${worksite ? `?worksite=${encodeURIComponent(worksite)}` : ''}`),
  timeseries: (days = 14, worksite?: string) =>
    get<{ series: SeriesPoint[] }>(
      `/api/analytics/timeseries?days=${days}${worksite ? `&worksite=${encodeURIComponent(worksite)}` : ''}`,
    ),
  violations: (limit = 50, worksite?: string) =>
    get<{ items: Violation[] }>(
      `/api/violations?limit=${limit}${worksite ? `&worksite=${encodeURIComponent(worksite)}` : ''}`,
    ),
  videos: async () => {
    const raw = await get<unknown>('/api/videos')
    return { items: normalizeVideos(raw) }
  },
  liveStatus: async (): Promise<LiveStatus> => {
    try {
      const s = await get<Partial<LiveStatus>>('/api/live/status')
      return {
        running: Boolean(s.running),
        source: s.source ?? null,
        profile: s.profile ?? null,
        fps: Number(s.fps ?? 0),
        frame: Number(s.frame ?? 0),
        workers: Number(s.workers ?? 0),
        forklifts: Number(s.forklifts ?? 0),
        forklift_speed_kmh: Number(s.forklift_speed_kmh ?? 0),
        forklift_speed_limit_kmh: Number(s.forklift_speed_limit_kmh ?? 8),
        forklift_overspeed: Boolean(s.forklift_overspeed),
        road_ways: Number(s.road_ways ?? 0),
        violations_session: Number(s.violations_session ?? 0),
        last_alert: s.last_alert ?? null,
        status: String(s.status ?? 'idle'),
        aisle_locked: Boolean(s.aisle_locked),
      }
    } catch {
      return {
        running: false,
        source: null,
        profile: null,
        fps: 0,
        frame: 0,
        workers: 0,
        forklifts: 0,
        forklift_speed_kmh: 0,
        forklift_speed_limit_kmh: 8,
        forklift_overspeed: false,
        road_ways: 0,
        violations_session: 0,
        last_alert: null,
        status: 'api-offline',
        aisle_locked: false,
      }
    }
  },
  liveStart: (source: string) => post<LiveStatus>('/api/live/start', { source }),
  liveStop: () => post<LiveStatus>('/api/live/stop'),

  /** Latest JPEG snapshot URL (preferred over MJPEG in Chrome). */
  frameUrl: () => `${resolveApiOrigin()}/api/live/frame.jpg?t=${Date.now()}`,

  /** MJPEG URL — localhost uses :8001 directly; ngrok uses same-origin Vite proxy. */
  streamUrl: () => `${resolveApiOrigin()}/api/live/stream?t=${Date.now()}`,
}
