import { useEffect, useState } from 'react'
import { api, type Violation } from '../api/client'

export function ReportsPage() {
  const [items, setItems] = useState<Violation[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.violations(100)
      .then((r) => setItems(r.items))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed'))
  }, [])

  return (
    <>
      <div className="breadcrumb">Home &gt; <strong>Reports</strong></div>
      <div className="card">
        <h3>Violation Report</h3>
        {error && <p className="error">{error}</p>}
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Event</th>
                <th>Severity</th>
                <th>Profile</th>
                <th>Worksite</th>
              </tr>
            </thead>
            <tbody>
              {items.map((v) => (
                <tr key={v.id}>
                  <td>{v.id}</td>
                  <td>{new Date(v.ts).toLocaleString()}</td>
                  <td>{v.event_type}</td>
                  <td><span className={`badge ${v.severity}`}>{v.severity}</span></td>
                  <td>{v.profile}</td>
                  <td>{v.worksite}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
