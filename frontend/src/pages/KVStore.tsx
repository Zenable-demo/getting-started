import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { KVStoreEntry } from '../types'

export default function KVStore() {
  const [entries, setEntries] = useState<KVStoreEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newKey, setNewKey] = useState<string>('')
  const [newValue, setNewValue] = useState<string>('')
  const [editingKey, setEditingKey] = useState<string | null>(null)

  useEffect(() => {
    const loadEntries = async () => {
      try {
        const data = await api.listKVStore()
        setEntries(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load KV store')
      } finally {
        setLoading(false)
      }
    }

    loadEntries()
  }, [])

  const handleAddOrUpdate = async () => {
    if (!newKey.trim() || !newValue.trim()) {
      setError('Key and value are required')
      return
    }

    try {
      await api.setKVValue(newKey, newValue)
      const data = await api.listKVStore()
      setEntries(data)
      setNewKey('')
      setNewValue('')
      setEditingKey(null)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save value')
    }
  }

  const handleDelete = async (key: string) => {
    if (!confirm(`Delete key "${key}"?`)) return

    try {
      await api.deleteKVValue(key)
      setEntries((prev) => prev.filter((e) => e.key !== key))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete value')
    }
  }

  const handleEdit = (entry: KVStoreEntry) => {
    setEditingKey(entry.key)
    setNewKey(entry.key)
    setNewValue(entry.value)
  }

  if (loading) return <div className="page loading">Loading KV store...</div>

  return (
    <div className="page">
      <h2>Key-Value Store</h2>
      {error && <div className="error">{error}</div>}

      <div style={{ background: '#f0f0f0', padding: '20px', borderRadius: '8px', marginBottom: '30px' }}>
        <h3 style={{ marginTop: 0 }}>{editingKey ? 'Edit Entry' : 'Add New Entry'}</h3>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>Key</label>
          <input
            type="text"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            disabled={editingKey !== null}
            style={{ width: '100%', maxWidth: '400px' }}
            placeholder="Enter key"
          />
        </div>
        <div style={{ marginBottom: '12px' }}>
          <label style={{ display: 'block', marginBottom: '4px', fontWeight: '500' }}>Value</label>
          <textarea
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            style={{ width: '100%', maxWidth: '400px', minHeight: '100px' }}
            placeholder="Enter value"
          />
        </div>
        <button onClick={handleAddOrUpdate} style={{ marginRight: '8px' }}>
          {editingKey ? 'Update' : 'Add'}
        </button>
        {editingKey && (
          <button
            onClick={() => {
              setEditingKey(null)
              setNewKey('')
              setNewValue('')
            }}
            style={{ background: '#666' }}
          >
            Cancel
          </button>
        )}
      </div>

      {entries.length > 0 ? (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Key</th>
                <th>Value</th>
                <th>Updated At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.key}>
                  <td>{entry.key}</td>
                  <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{entry.value}</td>
                  <td>{new Date(entry.updated_at).toLocaleString()}</td>
                  <td>
                    <button onClick={() => handleEdit(entry)} style={{ marginRight: '8px' }}>
                      Edit
                    </button>
                    <button onClick={() => handleDelete(entry.key)} style={{ background: '#e74c3c' }}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty">No entries yet</div>
      )}
    </div>
  )
}
