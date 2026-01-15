export interface ImageStack {
  id: string
  filename: string
  file_path: string
  file_size: number
  width: number
  height: number
  depth: number
  channels: number
  bit_depth: number
  pixel_size_x?: number
  pixel_size_y?: number
  pixel_size_z?: number
  acquisition_date?: string
  microscope_id?: string
  objective_info?: any
  channel_config?: any
  processing_status: 'uploaded' | 'processing' | 'completed' | 'failed'
  upload_date: string
  metadata?: any
}

export interface AnalysisResult {
  id: string
  stack_id: string
  algorithm_name: string
  algorithm_version: string
  gpu_device?: string
  processing_time_ms: number
  results: any
  confidence_score?: number
  human_validated: boolean
  validation_timestamp?: string
  validator_id?: string
  validation_notes?: string
  created_at: string
  updated_at: string
}

export interface ValidationStats {
  total_results: number
  validated_results: number
  pending_validation: number
  validation_rate: number
}

export interface AnalysisRequest {
  algorithm: string
  parameters?: Record<string, any>
}

export interface ValidationRequest {
  validated: boolean
  notes?: string
  validator_id?: string
}