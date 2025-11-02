export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
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
  data: T
  message?: string
  status: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface Prompt {
  id: number
  prompt_text: string
  prompt_hash: string
  total_uses: number
  total_fails: number
  first_used_at: string
  last_used_at: string
  model?: string
  thumbnail_mime?: string
  thumbnail_width?: number
  thumbnail_height?: number
}

export interface PromptListResponse {
  prompts: Prompt[]
  total: number
  page: number
  limit: number
}

export interface PromptStats {
  total_prompts: number
  total_uses: number
  total_fails: number
  prompts_with_thumbnails: number
  most_popular_prompt?: string
  most_popular_uses: number
  most_failed_prompt?: string
  most_failed_count: number
}

export interface QueueItem {
  id: string
  file: File
  preview: string
  style: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  prompt?: string
  thumbnail?: string
  error?: string
}
