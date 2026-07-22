import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Finding } from '../types'

export default function Findings() {
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('')

  useEffect(() => {
    const loadFindings = async () => {
      try {
        const data = await api.listFindings(100)
        setFindings(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load findings')
      } finally {
        setLoading(false)
      }
    }

    loadFindings()
  }, [])

  const handleDecision = async (findingId: string, decision: 'approve' | 'reject') => {
    try {
      await api.recordFindingDecision(findingId, decision)
      setFindings((prev) => prev.filter((f) => f.id !== findingId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record decision')
    }
  }

  const filtered = findings.filter(
    (f) =>
      f.pattern_name.toLowerCase().includes(filter.toLowerCase()) ||
      f.file_path.toLowerCase().includes(filter.toLowerCase())
  )

  if (loading) return <div className="page loading">Loading findings...</div>

  return (
    <div className="page">
      <h2>Findings</h2>
      {error && <div className="error">{error}</div>}

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Filter by pattern or file..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ width: '100%', maxWidth: '400px' }}
        />
      </div>

      {filtered.length > 0 ? (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>File</th>
                <th>Line</th>
                <th>Pattern</th>
                <th>Content</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((finding) => (
                <tr key={finding.id}>
                  <td>{finding.file_path}</td>
                  <td>{finding.line_number}</td>
                  <td>{finding.pattern_name}</td>
                  <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{finding.line_content}</td>
                  <td>
                    <button onClick={() => handleDecision(finding.id, 'approve')} style={{ marginRight: '8px' }}>
                      Approve
                    </button>
                    <button onClick={() => handleDecision(finding.id, 'reject')} style={{ background: '#e74c3c' }}>
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty">No findings found</div>
      )}
    </div>
  )
}
