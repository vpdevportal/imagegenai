import axios from 'axios'
import { Prompt, PromptListResponse, PromptStats } from '@/types'

// Use relative URL in production (works with Next.js rewrites) or fallback to env/localhost
// This prevents local network permission prompts when deployed
const getApiBaseUrl = () => {
  // In browser (client-side), always use relative URL to leverage Next.js rewrites
  // This avoids local network permission issues when deployed
  // The rewrite in next.config.js handles proxying to the backend
  if (typeof window !== 'undefined') {
    return '/api'
  }
  
  // Server-side: use environment variable if set, otherwise 127.0.0.1
  // Using 127.0.0.1 instead of localhost forces IPv4 and avoids IPv6 connection issues
  // This is for SSR/SSG scenarios (if any)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }
  
  return 'http://127.0.0.1:6001/api'
}

// Normalize image URLs to use relative paths to avoid local network permission issues
// Converts absolute localhost/internal URLs to relative URLs that go through Next.js proxy
export const normalizeImageUrl = (url: string | undefined | null): string => {
  if (!url || url === '/placeholder-image.jpg') {
    return '/placeholder-image.jpg'
  }

  // If already relative, return as-is
  if (url.startsWith('/')) {
    return url
  }

  try {
    const urlObj = new URL(url, typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000')
    
    // If it's a localhost or same-origin URL, convert to relative path
    // This ensures it goes through Next.js proxy instead of direct backend access
    if (urlObj.hostname === 'localhost' || 
        urlObj.hostname === '127.0.0.1' || 
        (typeof window !== 'undefined' && urlObj.hostname === window.location.hostname)) {
      // If it's an API endpoint, ensure it starts with /api
      if (urlObj.pathname.startsWith('/api/')) {
        return urlObj.pathname + urlObj.search
      }
      // Otherwise, return the pathname
      return urlObj.pathname + urlObj.search
    }
    
    // For external URLs, return as-is (they're safe)
    return url
  } catch (e) {
    // If URL parsing fails, assume it's already relative or return as-is
    return url
  }
}

const API_BASE_URL = getApiBaseUrl()

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

export const generateImage = async (
  prompt: string, 
  image: File, 
  provider?: string, 
  onRetry?: (attempt: number) => void,
  shouldCancel?: () => boolean,
  promptId?: number
): Promise<ImageGenerationResponse> => {
  console.log('generateImage API call - prompt:', `"${prompt}"`, 'length:', prompt.length, 'file:', image.name, 'provider:', provider, 'promptId:', promptId)

  let lastError: any
  let attempt = 0
  const maxRetries = 20

  while (attempt < maxRetries) {
    // Check if cancellation was requested
    if (shouldCancel && shouldCancel()) {
      console.log('Image generation cancelled by user')
      throw new Error('Image generation cancelled by user')
    }

    attempt++
    
    try {
      const formData = new FormData()
      formData.append('prompt', prompt) // Prompt is always required
      formData.append('image', image)
      if (provider) {
        formData.append('provider', provider)
      }
      if (promptId) {
        formData.append('prompt_id', promptId.toString())
      }

      console.log(`FormData contents - attempt ${attempt} - prompt:`, formData.get('prompt'), 'image:', formData.get('image'))

      const response = await api.post('/generate/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      console.log(`Image generation successful on attempt ${attempt}`)
      return response.data

    } catch (error: any) {
      // Check if this is a cancellation error (re-throw it)
      if (error?.message === 'Image generation cancelled by user') {
        throw error
      }

      lastError = error
      console.error(`Image generation attempt ${attempt} failed:`, error?.response?.data || error?.message)

      // Check if cancellation was requested after error
      if (shouldCancel && shouldCancel()) {
        console.log('Image generation cancelled by user after error')
        throw new Error('Image generation cancelled by user')
      }

      // Notify about retry attempt
      if (onRetry) {
        onRetry(attempt)
      }

      // Check if we've reached max retries - if so, throw immediately
      if (attempt >= maxRetries) {
        console.error(`Image generation failed after ${maxRetries} attempts`)
        throw lastError || new Error(`Image generation failed after ${maxRetries} attempts`)
      }

      // Exponential backoff: wait 1s, 2s, 4s, 8s, then cap at 8s between retries
      const delay = Math.min(Math.pow(2, attempt - 1) * 1000, 8000)
      console.log(`Waiting ${delay}ms before retry attempt ${attempt + 1}`)
      
      // Wait with cancellation check
      let cancelled = false
      const startTime = Date.now()
      while (Date.now() - startTime < delay) {
        if (shouldCancel && shouldCancel()) {
          cancelled = true
          break
        }
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      if (cancelled) {
        console.log('Image generation cancelled during wait')
        throw new Error('Image generation cancelled by user')
      }
    }
  }

  // This should never be reached due to the check inside the loop, but TypeScript needs this
  // to understand that the function always returns or throws
  throw lastError || new Error(`Image generation failed after ${maxRetries} attempts`)
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

export const getPrompt = async (promptId: number): Promise<Prompt> => {
  const response = await api.get(`/prompts/${promptId}`)
  return response.data
}

export const getPromptThumbnail = async (promptId: number): Promise<string> => {
  // Ensure we use relative URL to avoid local network permission issues
  const response = await api.get(`/prompts/${promptId}/thumbnail`, {
    responseType: 'blob'
  })

  // Create blob URL from the response - this is safe and doesn't trigger network permissions
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
export const generatePromptFromImage = async (file: File, provider?: string): Promise<{
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
  if (provider) {
    formData.append('provider', provider)
  }

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
export const generateVariation = async (file: File, prompt?: string, provider?: string): Promise<{
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
  if (provider) {
    formData.append('provider', provider)
  }

  const response = await api.post('/variations/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Fusion API - Merge Two People Together
export const generateFusion = async (image1: File, image2: File, provider?: string): Promise<{
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
  if (provider) {
    formData.append('provider', provider)
  }

  const response = await api.post('/fusion/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Teleport API - Teleport Person to Background
export const generateTeleport = async (backgroundImage: File, personImage: File, provider?: string): Promise<{
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
  if (provider) {
    formData.append('provider', provider)
  }

  const response = await api.post('/teleport/generate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Grouping API - Generate Image with Multiple Person Images
export const generateGrouping = async (
  prompt: string,
  images: File[],
  provider?: string,
  onRetry?: (attempt: number) => void,
  shouldCancel?: () => boolean,
  promptId?: number
): Promise<ImageGenerationResponse> => {
  let lastError: any
  let attempt = 0
  const maxRetries = 20

  while (attempt < maxRetries) {
    if (shouldCancel && shouldCancel()) {
      throw new Error('Image generation cancelled by user')
    }

    attempt++

    try {
      const formData = new FormData()
      formData.append('prompt', prompt)
      images.forEach((image) => {
        formData.append('images', image)
      })
      if (provider) {
        formData.append('provider', provider)
      }
      if (promptId) {
        formData.append('prompt_id', promptId.toString())
      }

      const response = await api.post('/grouping/generate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      return response.data
    } catch (error: any) {
      if (error?.message === 'Image generation cancelled by user') {
        throw error
      }

      lastError = error

      if (shouldCancel && shouldCancel()) {
        throw new Error('Image generation cancelled by user')
      }

      if (onRetry) {
        onRetry(attempt)
      }

      if (attempt >= maxRetries) {
        throw lastError || new Error(`Image generation failed after ${maxRetries} attempts`)
      }

      const delay = Math.min(Math.pow(2, attempt - 1) * 1000, 8000)
      let cancelled = false
      const startTime = Date.now()
      while (Date.now() - startTime < delay) {
        if (shouldCancel && shouldCancel()) {
          cancelled = true
          break
        }
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      if (cancelled) {
        throw new Error('Image generation cancelled by user')
      }
    }
  }

  throw lastError || new Error(`Image generation failed after ${maxRetries} attempts`)
}

export default api