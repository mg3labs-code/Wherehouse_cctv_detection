import { Component, type ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, fontFamily: 'Segoe UI, sans-serif', maxWidth: 720 }}>
          <h1 style={{ color: '#dc2626' }}>Dashboard failed to load</h1>
          <pre style={{ background: '#f3f4f6', padding: 12, overflow: 'auto' }}>
            {this.state.error.message}
          </pre>
          <p>Open DevTools (F12) → Console for details. Ensure API is running: <code>python run_api.py</code> (port 8001).</p>
          <button type="button" onClick={() => window.location.assign('/')}>
            Reload home
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
