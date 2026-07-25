import { useEffect, useMemo, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from 'recharts'
import { api, type Summary, type SeriesPoint } from '../api/client'
import {
  IconClock,
  IconCube,
  IconFilter,
  IconForklift,
  IconHardhat,
  IconImpact,
} from '../components/icons'

function fmt(n: number) {
  return new Intl.NumberFormat('en-US').format(n)
}

function formatDateLabel(iso: string) {
  const d = new Date(`${iso}T12:00:00`)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

export function SafetyAnalyticsPage() {
  const [worksite, setWorksite] = useState('all')
  const [worksites, setWorksites] = useState<string[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [series, setSeries] = useState<SeriesPoint[]>([])
  const [dateVal, setDateVal] = useState(() => new Date().toISOString().slice(0, 10))
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const wsParam = worksite === 'all' ? undefined : worksite

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [ws, sum, ts] = await Promise.all([
        api.worksites(),
        api.summary(wsParam),
        api.timeseries(14, wsParam),
      ])
      setWorksites(ws.worksites)
      setSummary(sum)
      setSeries(ts.series)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 15000)
    return () => clearInterval(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [worksite])

  const delta = useMemo(() => {
    if (series.length < 2) return 0
    const mid = Math.floor(series.length / 2)
    const a = series.slice(0, mid).reduce((s, p) => s + p.incidents, 0)
    const b = series.slice(mid).reduce((s, p) => s + p.incidents, 0)
    if (a === 0) return 0
    return Math.round(((b - a) / a) * 100)
  }, [series])

  return (
    <>
      <div className="breadcrumb">
        Home <span className="bc-sep">&gt;</span> <strong>Analytics</strong>
      </div>

      <div className="tabs-row">
        <div className="tabs">
          <button type="button" className="tab">
            Inspection Analytics
          </button>
          <button type="button" className="tab active">
            Safety Analytics
          </button>
        </div>
        <span className={`status-online ${summary?.online ? '' : 'offline'}`}>
          <span className="dot" />
          {summary?.online ? 'Online' : 'Offline'}
        </span>
      </div>

      <div className="filters">
        <div className="filter-row">
          <div className="filter-field grow">
            <select value={worksite} onChange={(e) => setWorksite(e.target.value)}>
              <option value="all">--All Worksites--</option>
              {worksites.map((w) => (
                <option key={w} value={w}>
                  {w}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-field daily">
            <label>Daily View</label>
            <div className="date-wrap">
              <input
                type="date"
                value={dateVal}
                onChange={(e) => setDateVal(e.target.value)}
                aria-label="Daily view date"
              />
              <span className="date-display">{formatDateLabel(dateVal)}</span>
            </div>
          </div>
          <button type="button" className="btn btn-filters" onClick={load}>
            <IconFilter />
            FILTERS
          </button>
        </div>
        <div className="filter-row secondary">
          <div className="filter-field">
            <label>Filter by</label>
            <select defaultValue="assets">
              <option value="assets">Assets</option>
              <option value="operators">Operators</option>
              <option value="alerts">Alerts</option>
            </select>
          </div>
          <div className="filter-field">
            <label>Select Asset</label>
            <select defaultValue="all">
              <option value="all">All Assets</option>
              <option value="forklift">Forklifts</option>
              <option value="cameras">Cameras</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <p className="error">
          Backend: {error}. Start API with: <code>python run_api.py</code> (port 8001)
        </p>
      )}
      {loading && !summary && <p className="muted">Loading analytics…</p>}

      {summary && (
        <div className="kpi-row">
          <div className="kpi">
            <div className="kpi-text">
              <div className="label">Safety Score</div>
              <div className="value green">{summary.safety_score}%</div>
              <div className="meta">{summary.safety_label}</div>
            </div>
            <div className="kpi-ico">
              <IconForklift />
            </div>
          </div>
          <div className="kpi">
            <div className="kpi-text">
              <div className="label">Incidents Prevented</div>
              <div className="value">{fmt(summary.incidents_prevented)}</div>
            </div>
            <div className="kpi-ico">
              <IconImpact />
            </div>
          </div>
          <div className="kpi">
            <div className="kpi-text">
              <div className="label">Asset Hours</div>
              <div className="value">{fmt(summary.asset_hours)}</div>
            </div>
            <div className="kpi-ico">
              <IconClock />
            </div>
          </div>
          <div className="kpi">
            <div className="kpi-text">
              <div className="label">Assets</div>
              <div className="value">{summary.assets}</div>
            </div>
            <div className="kpi-ico">
              <IconCube />
            </div>
          </div>
          <div className="kpi">
            <div className="kpi-text">
              <div className="label">Operators</div>
              <div className="value">{summary.operators}</div>
            </div>
            <div className="kpi-ico">
              <IconHardhat />
            </div>
          </div>
        </div>
      )}

      <div className="grid-2">
        <div className="card chart-card">
          <div className="chart-head">
            <h3>Safety Stats</h3>
            <div className="legend-inline">
              <span>
                <i className="lg blue" /> Incidents Prevented
              </span>
              <span>
                <i className="lg teal" /> Overrides Pressed
              </span>
              <span>
                <i className="lg purple" /> Emergency Stops
              </span>
            </div>
          </div>
          <div className="chart-body">
            <div className="chart-callout">
              {delta <= 0 ? `${Math.abs(delta)}% ↓` : `${delta}% ↑`} Incidents since prior period
            </div>
            <div className="chart-plot">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={series} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e6ebf2" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11, fill: '#8a94a6' }}
                    tickFormatter={(v) => String(v).slice(5)}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: '#8a94a6' }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip />
                  <Legend content={() => null} />
                  <Line
                    type="monotone"
                    dataKey="incidents"
                    name="Incidents Prevented"
                    stroke="#1e5bb8"
                    strokeWidth={2.5}
                    dot={{ r: 3, fill: '#1e5bb8' }}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="overrides"
                    name="Overrides Pressed"
                    stroke="#5ec8d8"
                    strokeWidth={2.5}
                    dot={{ r: 3, fill: '#5ec8d8' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="emergency"
                    name="Emergency Stops"
                    stroke="#5b4db8"
                    strokeWidth={2.5}
                    dot={{ r: 3, fill: '#5b4db8' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="card chart-card">
          <div className="chart-head">
            <h3>Alert Volume</h3>
            <div className="legend-inline">
              <span>
                <i className="lg blue" /> Daily Alerts
              </span>
            </div>
          </div>
          <div className="chart-body">
            <div className="chart-plot">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={series} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e6ebf2" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11, fill: '#8a94a6' }}
                    tickFormatter={(v) => String(v).slice(5)}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: '#8a94a6' }}
                    axisLine={false}
                    tickLine={false}
                    allowDecimals={false}
                  />
                  <Tooltip />
                  <Bar
                    dataKey="incidents"
                    name="Daily Alerts"
                    fill="#2f6fdb"
                    radius={[3, 3, 0, 0]}
                    maxBarSize={36}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
