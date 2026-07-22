import type {
  Finding,
  HealthResponse,
  KVStoreEntry,
  ScanRequest,
  ScanResponse,
  ScanStatus,
  WebhookSubscription,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const API_KEY = import.meta.env.VITE_API_KEY || 'demo-key-12345'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || `API error: ${response.status}`)
  }
  return response.json()
}

export const api = {
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/healthz`, {
      headers,
    })
    return handleResponse(response)
  },

  async triggerScan(path: string): Promise<ScanResponse> {
    const response = await fetch(`${API_BASE_URL}/scans`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ path }),
    })
    return handleResponse(response)
  },

  async getScanStatus(jobId: string): Promise<ScanStatus> {
    const response = await fetch(`${API_BASE_URL}/scans/${jobId}`, {
      headers,
    })
    return handleResponse(response)
  },

  async listFindings(limit = 100): Promise<Finding[]> {
    const response = await fetch(`${API_BASE_URL}/findings?limit=${limit}`, {
      headers,
    })
    return handleResponse(response)
  },

  async recordFindingDecision(
    findingId: string,
    decision: 'approve' | 'reject',
    note?: string
  ): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/findings/${findingId}/decision`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ decision, note }),
    })
    return handleResponse(response)
  },

  async listKVStore(): Promise<KVStoreEntry[]> {
    const response = await fetch(`${API_BASE_URL}/kv`, {
      headers,
    })
    return handleResponse(response)
  },

  async getKVValue(key: string): Promise<KVStoreEntry> {
    const response = await fetch(`${API_BASE_URL}/kv/${key}`, {
      headers,
    })
    return handleResponse(response)
  },

  async setKVValue(key: string, value: string): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/kv/${key}`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ value }),
    })
    return handleResponse(response)
  },

  async deleteKVValue(key: string): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/kv/${key}`, {
      method: 'DELETE',
      headers,
    })
    return handleResponse(response)
  },

  async listWebhooks(): Promise<WebhookSubscription[]> {
    const response = await fetch(`${API_BASE_URL}/webhooks`, {
      headers,
    })
    return handleResponse(response)
  },
}
