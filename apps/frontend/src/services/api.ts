import axios from 'axios'
import { Prompt, PromptListResponse, PromptStats } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for image generation
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Disable credentials for CORS
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface ImageGenerationResponse {
  id: string
  message: string
  prompt: string
  status: string
  generated_image_url?: string
  reference_image_url?: string
  created_at: string
  estimated_completion_time?: number
}

// API functions

export const generateImage = async (prompt: string, image: File, onRetry?: (attempt: number, maxAttempts: number) => void): Promise<ImageGenerationResponse> => {
  console.log('generateImage API call - prompt:', `"${prompt}"`, 'length:', prompt.length, 'file:', image.name)

  const maxRetries = 3
  let lastError: any

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const formData = new FormData()
      formData.append('prompt', prompt)
      formData.append('image', image)

      console.log(`FormData contents - attempt ${attempt}/${maxRetries} - prompt:`, formData.get('prompt'), 'image:', formData.get('image'))

      const response = await api.post('/generate/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      console.log(`Image generation successful on attempt ${attempt}`)
      return response.data

    } catch (error: any) {
      lastError = error
      console.error(`Image generation attempt ${attempt}/${maxRetries} failed:`, error?.response?.data || error?.message)

      // Notify about retry attempt
      if (onRetry) {
        onRetry(attempt, maxRetries)
      }

      // If this is the last attempt, don't wait
      if (attempt === maxRetries) {
        break
      }

      // Exponential backoff: wait 1s, 2s, 4s, 8s between retries
      const delay = Math.pow(2, attempt - 1) * 1000
      console.log(`Waiting ${delay}ms before retry attempt ${attempt + 1}`)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  // If we get here, all retries failed
  console.error(`Image generation failed after ${maxRetries} attempts`)
  throw lastError
}

// Prompt API functions
export const getPrompts = async (page = 1, limit = 100, model?: string, sortBy = 'recent'): Promise<PromptListResponse> => {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
    sort_by: sortBy
  })

  if (model) {
    params.append('model', model)
  }

  const response = await api.get(`/prompts/?${params}`)
  return response.data
}

export const getPopularPrompts = async (limit = 100, model?: string): Promise<Prompt[]> => {
  const params = new URLSearchParams({ limit: limit.toString() })
  if (model) {
    params.append('model', model)
  }

  const response = await api.get(`/prompts/popular?${params}`)
  return response.data
}

export const getRecentPrompts = async (limit = 100, model?: string): Promise<Prompt[]> => {
  const params = new URLSearchParams({ limit: limit.toString() })
  if (model) {
    params.append('model', model)
  }

  const response = await api.get(`/prompts/recent?${params}`)
  return response.data
}

export const getMostFailedPrompts = async (limit = 100, model?: string): Promise<Prompt[]> => {
  const params = new URLSearchParams({ limit: limit.toString() })
  if (model) {
    params.append('model', model)
  }

  const response = await api.get(`/prompts/most-failed?${params}`)
  return response.data
}

export const searchPrompts = async (query: string, limit = 20): Promise<Prompt[]> => {
  const params = new URLSearchParams({
    query,
    limit: limit.toString()
  })

  const response = await api.get(`/prompts/search?${params}`)
  return response.data
}

export const getPromptStats = async (): Promise<PromptStats> => {
  const response = await api.get('/prompts/stats/overview')
  return response.data
}

export const getPromptThumbnail = async (promptId: number): Promise<string> => {
  const response = await api.get(`/prompts/${promptId}/thumbnail`, {
    responseType: 'blob'
  })

  return URL.createObjectURL(response.data)
}

export const deletePrompt = async (promptId: number): Promise<{ message: string }> => {
  const response = await api.delete(`/prompts/${promptId}`)
  return response.data
}

export const savePrompt = async (prompt: string): Promise<Prompt> => {
  const formData = new FormData()
  formData.append('prompt', prompt)

  const apiResponse = await api.post('/prompts/save', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return apiResponse.data
}

// Inspire API - Image to Prompt Generation
export const generatePromptFromImage = async (file: File): Promise<{
  success: boolean
  prompt: string
  style: string
  thumbnail: string
  original_filename: string
  prompt_id: number | null
  saved_to_database: boolean
}> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/inspire/generate-prompt', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Track prompt usage
export const trackPromptUsage = async (promptId: number): Promise<Prompt> => {
  const response = await api.post(`/prompts/${promptId}/use`)
  return response.data
}

// Variations API - Image Variation Generation
export const generateVariation = async (file: File, prompt?: string): Promise<{
  id: string
  message: string
  prompt: string
  original_prompt: string | null
  status: string
  generated_image_url: string
  reference_image_url: string
  created_at: string
}> => {
  const formData = new FormData()
  formData.append('file', file)
  if (prompt && prompt.trim()) {
    formData.append('prompt', prompt.trim())
  }

  const response = await api.post('/variations/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Fusion API - Merge Two People Together
export const generateFusion = async (image1: File, image2: File): Promise<{
  id: string
  message: string
  prompt: string
  status: string
  generated_image_url: string
  reference_image_url: string
  created_at: string
}> => {
  const formData = new FormData()
  formData.append('image1', image1)
  formData.append('image2', image2)

  const response = await api.post('/fusion/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Teleport API - Teleport Person to Background
export const generateTeleport = async (backgroundImage: File, personImage: File): Promise<{
  id: string
  message: string
  prompt: string
  status: string
  generated_image_url: string
  reference_image_url: string
  created_at: string
}> => {
  const formData = new FormData()
  formData.append('background_image', backgroundImage)
  formData.append('person_image', personImage)

  const response = await api.post('/teleport/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export default api