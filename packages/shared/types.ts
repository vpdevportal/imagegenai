export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface Image {
  id: number
  prompt: string
  generated_image_url?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at?: string
  user_id?: number
  metadata_json?: string
}

export interface ImageCreateRequest {
  prompt: string
  user_id?: number
  metadata?: Record<string, any>
}

export interface ApiResponse<T> {
  data?: T
  message?: string
  status: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy'
  message: string
  timestamp: string
  version?: string
}
