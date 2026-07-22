import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { HealthResponse, Finding } from '../types'

export default function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [healthData, findingsData] = await Promise.all([
          api.health(),
          api.listFindings(10),
        ])
        setHealth(healthData)
        setFindings(findingsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  if (loading) return <div className="page loading">Loading dashboard...</div>

  const patternCounts: { [key: string]: number } = {}
  findings.forEach((f) => {
    patternCounts[f.pattern_name] = (patternCounts[f.pattern_name] || 0) + 1
  })

  return (
    <div className="page">
      <h2>Dashboard</h2>
      {error && <div className="error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div style={{ background: '#f0f0f0', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#4a9eff' }}>{findings.length}</div>
          <div style={{ color: '#666', marginTop: '8px' }}>Total Findings</div>
        </div>
        <div style={{ background: '#f0f0f0', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#4a9eff' }}>{Object.keys(patternCounts).length}</div>
          <div style={{ color: '#666', marginTop: '8px' }}>Pattern Types</div>
        </div>
        <div style={{ background: '#f0f0f0', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#4a9eff' }}>{health?.status === 'ok' ? '✓' : '✗'}</div>
          <div style={{ color: '#666', marginTop: '8px' }}>API Status</div>
        </div>
      </div>

      <h3>Recent Findings by Pattern</h3>
      {Object.keys(patternCounts).length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {Object.entries(patternCounts).map(([pattern, count]) => (
            <li key={pattern} style={{ padding: '8px 0', borderBottom: '1px solid #eee' }}>
              <strong>{pattern}:</strong> {count} finding{count !== 1 ? 's' : ''}
            </li>
          ))}
        </ul>
      ) : (
        <div className="empty">No findings yet</div>
      )}
    </div>
  )
}
