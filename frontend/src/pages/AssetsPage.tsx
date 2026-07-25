import { useEffect, useState } from 'react'
import { api, type VideoItem } from '../api/client'

export function AssetsPage() {
  const [videos, setVideos] = useState<VideoItem[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.videos()
      .then((r) => setVideos(r.items))
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed'))
  }, [])

  return (
    <>
      <div className="breadcrumb">Home &gt; <strong>Inspect Asset</strong></div>
      <div className="card">
        <h3>Camera / Video Assets</h3>
        {error && <p className="error">{error}</p>}
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Path</th>
                <th>Size</th>
              </tr>
            </thead>
            <tbody>
              {videos.map((v) => (
                <tr key={v.path}>
                  <td>{v.id}</td>
                  <td>{v.name}</td>
                  <td className="muted">{v.path}</td>
                  <td>{v.size_mb} MB</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
