import { useState } from 'react'
import { api } from '../api/client'
import type { ScanResponse, ScanStatus } from '../types'

interface ScanJob {
  jobId: string
  path: string
  status: ScanStatus
}

export default function Scans() {
  const [scanPath, setScanPath] = useState<string>('.')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobs, setJobs] = useState<ScanJob[]>([])

  const handleTriggerScan = async () => {
    if (!scanPath.trim()) {
      setError('Scan path is required')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response: ScanResponse = await api.triggerScan(scanPath)
      const newJob: ScanJob = {
        jobId: response.job_id,
        path: response.path,
        status: {
          scan_dir: response.path,
          status: response.status,
        },
      }
      setJobs((prev) => [newJob, ...prev])

      // Poll for status updates
      const pollInterval = setInterval(async () => {
        try {
          const status = await api.getScanStatus(response.job_id)
          setJobs((prev) =>
            prev.map((job) => (job.jobId === response.job_id ? { ...job, status } : job))
          )

          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(pollInterval)
          }
        } catch (err) {
          console.error('Failed to poll status:', err)
          clearInterval(pollInterval)
        }
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger scan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h2>Scans</h2>
      {error && <div className="error">{error}</div>}

      <div style={{ background: '#f0f0f0', padding: '20px', borderRadius: '8px', marginBottom: '30px' }}>
        <h3 style={{ marginTop: 0 }}>Trigger New Scan</h3>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>Directory Path</label>
          <input
            type="text"
            value={scanPath}
            onChange={(e) => setScanPath(e.target.value)}
            placeholder="Enter directory path (e.g., .)"
            style={{ width: '100%', maxWidth: '400px' }}
          />
        </div>
        <button onClick={handleTriggerScan} disabled={loading}>
          {loading ? 'Triggering...' : 'Trigger Scan'}
        </button>
      </div>

      {jobs.length > 0 ? (
        <div>
          <h3>Scan History</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Path</th>
                  <th>Status</th>
                  <th>Findings</th>
                  <th>Completed At</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.jobId}>
                    <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{job.jobId.slice(0, 8)}...</td>
                    <td>{job.path}</td>
                    <td>
                      <span
                        className={`status-badge status-${job.status.status}`}
                      >
                        {job.status.status}
                      </span>
                    </td>
                    <td>{job.status.result?.total_findings || 0}</td>
                    <td>{job.status.completed_at ? new Date(job.status.completed_at).toLocaleString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="empty">No scans yet. Trigger one to get started!</div>
      )}
    </div>
  )
}
