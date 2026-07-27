import { Suspense, useEffect, useState, type ReactNode } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { api } from '../api/client'
import {
  IconChart,
  IconChecklist,
  IconChevron,
  IconDoc,
  IconFlag,
  IconHelp,
  IconLive,
  IconOrg,
  IconPower,
  IconScan,
  IconSliders,
} from './icons'

type NavItem = {
  to?: string
  label: string
  icon: ReactNode
  end?: boolean
  chevron?: boolean
  action?: () => void
}

const primary: NavItem[] = [
  { to: '/assets', label: 'Inspect Asset', icon: <IconScan /> },
  { to: '/', label: 'Analytics', icon: <IconChart />, end: true, chevron: true },
  { to: '/live', label: 'Live Monitor', icon: <IconLive /> },
  { to: '/reports', label: 'Reports', icon: <IconDoc />, chevron: true },
  { label: 'Checklist Settings', icon: <IconChecklist /> },
  { label: 'Management', icon: <IconOrg />, chevron: true },
  { to: '/settings', label: 'Settings', icon: <IconSliders />, chevron: true },
  { label: 'Help Center', icon: <IconHelp /> },
  { label: 'Logout', icon: <IconPower /> },
]

export function Layout() {
  const [apiOk, setApiOk] = useState<boolean | null>(null)

  useEffect(() => {
    let cancelled = false
    const tick = () => {
      api.ping().then((ok) => {
        if (!cancelled) setApiOk(ok)
      })
    }
    tick()
    const id = setInterval(tick, 5000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="user-block">
          <div className="brand-logo" aria-hidden>
            <img src="/contracto-logo.png" alt="CONTRACTO" width={168} height={72} />
          </div>
          <strong className="user-name">Safety Admin</strong>
          <span className="user-org">Hypervis Warehouse</span>
          <span className="user-role">Account Owner</span>
        </div>

        <nav className="nav">
          {primary.map((item) => {
            const body = (
              <>
                <span className="nav-ico">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
                {item.chevron && (
                  <span className="nav-chevron">
                    <IconChevron />
                  </span>
                )}
              </>
            )
            if (item.to) {
              return (
                <NavLink
                  key={item.label}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `nav-item${isActive ? ' active' : ''}`
                  }
                >
                  {body}
                </NavLink>
              )
            }
            return (
              <button key={item.label} type="button" className="nav-item nav-btn">
                {body}
              </button>
            )
          })}
        </nav>
      </aside>

      <div className="main">
        <header className="topbar">
          <h2>Hypervis.AI Dashboard</h2>
          <div className="topbar-right">
            <button type="button" className="lang-btn" title="Language">
              <IconFlag />
              <span>EN</span>
            </button>
            <button type="button" className="icon-btn" title="Help" aria-label="Help">
              <IconHelp />
            </button>
          </div>
        </header>

        {apiOk === false && (
          <div className="api-banner">
            Backend not reachable. Start it with <code>python run_api.py</code> (port{' '}
            <strong>8001</strong>), then refresh.
          </div>
        )}

        <div className="content">
          <Suspense fallback={<p className="muted">Loading page…</p>}>
            <Outlet />
          </Suspense>
        </div>
      </div>
    </div>
  )
}
