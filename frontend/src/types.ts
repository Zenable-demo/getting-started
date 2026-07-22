export interface Finding {
  id: string
  file_path: string
  line_number: number
  pattern_name: string
  line_content: string
  scanned_at: string
}

export interface ScanRequest {
  path: string
}

export interface ScanResponse {
  job_id: string
  status: string
  path: string
}

export interface ScanStatus {
  scan_dir: string
  status: string
  total_findings?: number
  completed_at?: string
  result?: {
    scan_directory: string
    total_findings: number
  }
}

export interface KVStoreEntry {
  key: string
  value: string
  updated_at: string
}

export interface WebhookSubscription {
  id: string
  url: string
  event_types: string
  active: boolean
  created_at: string
}

export interface HealthResponse {
  status: string
  version: string
}
