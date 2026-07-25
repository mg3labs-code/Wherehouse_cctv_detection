import { Navigate, Route, Routes } from 'react-router-dom'
import { lazy } from 'react'
import { Layout } from './components/Layout'

const SafetyAnalyticsPage = lazy(() =>
  import('./pages/SafetyAnalyticsPage').then((m) => ({ default: m.SafetyAnalyticsPage })),
)
const LiveMonitorPage = lazy(() =>
  import('./pages/LiveMonitorPage').then((m) => ({ default: m.LiveMonitorPage })),
)
const ReportsPage = lazy(() =>
  import('./pages/ReportsPage').then((m) => ({ default: m.ReportsPage })),
)
const AssetsPage = lazy(() =>
  import('./pages/AssetsPage').then((m) => ({ default: m.AssetsPage })),
)
const SettingsPage = lazy(() =>
  import('./pages/SettingsPage').then((m) => ({ default: m.SettingsPage })),
)

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<SafetyAnalyticsPage />} />
        <Route path="live" element={<LiveMonitorPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="assets" element={<AssetsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
