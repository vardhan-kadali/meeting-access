import { useState, useEffect } from 'react'

interface HealthResponse {
  status: string
  service: string
  version: string
  timestamp: string
  python_version: string
  configured_gemini_model: string
  api_key_configured: boolean
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const checkHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/health')
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      }
      const data = await res.json()
      setHealth(data)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to connect to backend API.')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkHealth()
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      color: '#0f172a',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      padding: '2rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      <header style={{
        maxWidth: '800px',
        width: '100%',
        marginBottom: '2rem',
        textAlign: 'center'
      }}>
        <div style={{
          display: 'inline-block',
          backgroundColor: '#0f172a',
          color: '#ffffff',
          padding: '0.35rem 0.85rem',
          borderRadius: '9999px',
          fontSize: '0.8rem',
          fontWeight: 600,
          letterSpacing: '0.05em',
          marginBottom: '1rem',
          textTransform: 'uppercase'
        }}>
          Milestone 1 — Environment Verified
        </div>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 800,
          color: '#0f172a',
          margin: '0 0 0.5rem 0',
          letterSpacing: '-0.025em'
        }}>
          MEETING ACCESS
        </h1>
        <p style={{
          fontSize: '1.25rem',
          color: '#475569',
          margin: 0,
          fontWeight: 400
        }}>
          Know if you can participate before the meeting begins.
        </p>
      </header>

      <main style={{
        maxWidth: '800px',
        width: '100%',
        backgroundColor: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: '0.75rem',
        padding: '2rem',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
      }}>
        <section aria-labelledby="status-heading" style={{ marginBottom: '2rem' }}>
          <h2 id="status-heading" style={{
            fontSize: '1.25rem',
            fontWeight: 700,
            margin: '0 0 1rem 0',
            color: '#1e293b'
          }}>
            Backend System Health & Verification
          </h2>

          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', alignItems: 'center' }}>
            <button
              onClick={checkHealth}
              disabled={loading}
              style={{
                backgroundColor: '#1e3a8a',
                color: '#ffffff',
                border: 'none',
                padding: '0.6rem 1.2rem',
                borderRadius: '0.375rem',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading ? 'Querying /api/health...' : 'Recheck /api/health'}
            </button>
            <span style={{ fontSize: '0.9rem', color: '#64748b' }}>
              Target: <code>http://localhost:8000/api/health</code>
            </span>
          </div>

          {error && (
            <div role="alert" style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              color: '#991b1b',
              padding: '1rem',
              borderRadius: '0.5rem',
              fontSize: '0.95rem',
              marginBottom: '1rem'
            }}>
              <strong>Backend Offline or Unreachable:</strong> {error}
              <div style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
                Ensure FastAPI is running: <code>uvicorn app.main:app --port 8000</code> inside <code>backend/.venv</code>.
              </div>
            </div>
          )}

          {health && (
            <div style={{
              backgroundColor: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: '0.5rem',
              padding: '1.25rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <span style={{
                  display: 'inline-block',
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: '#16a34a'
                }} />
                <span style={{ fontWeight: 700, color: '#166534', fontSize: '1rem' }}>
                  Backend Status: {health.status.toUpperCase()}
                </span>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '0.75rem',
                fontSize: '0.9rem'
              }}>
                <div><strong>Service:</strong> {health.service}</div>
                <div><strong>API Version:</strong> {health.version}</div>
                <div><strong>Python Version:</strong> {health.python_version}</div>
                <div><strong>Configured Model:</strong> <code>{health.configured_gemini_model}</code></div>
                <div><strong>API Key Status:</strong> {health.api_key_configured ? 'Configured in .env' : 'Pending in .env'}</div>
                <div><strong>Timestamp:</strong> {new Date(health.timestamp).toLocaleTimeString()}</div>
              </div>
            </div>
          )}
        </section>

        <section aria-labelledby="milestone-heading" style={{
          borderTop: '1px solid #e2e8f0',
          paddingTop: '1.5rem'
        }}>
          <h2 id="milestone-heading" style={{
            fontSize: '1.1rem',
            fontWeight: 700,
            margin: '0 0 0.75rem 0',
            color: '#1e293b'
          }}>
            Milestone 1 Completion Checklist
          </h2>
          <ul style={{
            margin: 0,
            paddingLeft: '1.25rem',
            fontSize: '0.925rem',
            color: '#334155',
            lineHeight: 1.7
          }}>
            <li>Monorepo structure initialized (<code>frontend/</code>, <code>backend/app/</code>, <code>backend/tests/</code>).</li>
            <li>Git repository initialized at root with comprehensive <code>.gitignore</code>.</li>
            <li>Isolated Python 3.11 virtual environment configured at <code>backend/.venv</code>.</li>
            <li>FastAPI backend scaffolded with operational <code>/api/health</code> endpoint.</li>
            <li>React 19 + TypeScript + Vite frontend configured with reverse proxy to <code>:8000</code>.</li>
            <li>Official Google Gen AI SDK (<code>google-genai</code>) installed with configurable model ID.</li>
          </ul>
        </section>
      </main>

      <footer style={{
        marginTop: '2rem',
        fontSize: '0.85rem',
        color: '#64748b',
        textAlign: 'center'
      }}>
        MEETING ACCESS &bull; Bridge The Gap Hacks &bull; Civic Accessibility Intelligence
      </footer>
    </div>
  )
}
