'use client'

import { useState, useRef, useEffect } from 'react'
import { SparklesIcon, PhotoIcon, ArrowUpTrayIcon, XMarkIcon } from '@heroicons/react/24/outline'
import Image from 'next/image'
import { generateImage } from '@/services/api'

interface ImageGenerationFormProps {
  onImageGenerated: (image: any) => void
  isGenerating: boolean
  setIsGenerating: (value: boolean) => void
  initialPrompt?: string
}

export default function ImageGenerationForm({ 
  onImageGenerated, 
  isGenerating, 
  setIsGenerating,
  initialPrompt = ''
}: ImageGenerationFormProps) {
  const [prompt, setPrompt] = useState(initialPrompt)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [retryAttempt, setRetryAttempt] = useState(0)
  const [maxRetries, setMaxRetries] = useState(3)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Debug component mount
  useEffect(() => {
    console.log('ImageGenerationForm mounted - initialPrompt:', `"${initialPrompt}"`, 'prompt:', `"${prompt}"`)
  }, [])

  // Update prompt when initialPrompt prop changes
  useEffect(() => {
    console.log('useEffect triggered - initialPrompt:', `"${initialPrompt}"`, 'current prompt:', `"${prompt}"`)
    if (initialPrompt) {
      console.log('Setting prompt to:', `"${initialPrompt}"`)
      setPrompt(initialPrompt)
    }
  }, [initialPrompt])

  const handleFileSelect = (file: File) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      setError('Please select a valid image file (JPEG, PNG, or WebP)')
      return
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size is 10MB')
      return
    }

    setSelectedFile(file)
    setError('')
    
    // Create preview URL
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const clearImage = () => {
    setSelectedFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    // Clear any previous errors
    setError('')
    
    // Debug logging
    console.log('Form submission - prompt:', `"${prompt}"`, 'length:', prompt.length, 'selectedFile:', selectedFile)
    
    if (!prompt.trim()) {
      console.log('Validation failed: Empty prompt')
      setError('Please enter a prompt')
      return
    }

    if (prompt.length > 1000) {
      console.log('Validation failed: Prompt too long')
      setError('Prompt too long (max 1000 characters)')
      return
    }

    if (!selectedFile) {
      console.log('Validation failed: No file selected')
      setError('Please select a reference image')
      return
    }

    setError('')
    setRetryAttempt(0)
    setIsGenerating(true)

    try {
      console.log('Calling generateImage API with prompt:', `"${prompt}"`, 'file:', selectedFile.name)
      const response = await generateImage(prompt, selectedFile, (attempt, maxAttempts) => {
        setRetryAttempt(attempt)
        setMaxRetries(maxAttempts)
      })
      
      onImageGenerated({
        id: response.id,
        prompt,
        imageUrl: response.generated_image_url || '/placeholder-image.jpg',
        referenceImageUrl: response.reference_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: 'generation-with-reference'
      })
    } catch (err: any) {
      console.error('Image generation error:', err)
      
      // Extract specific error message from API response
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to generate image after multiple attempts. Please try again.'
      setError(errorMessage)
    } finally {
      setIsGenerating(false)
      setRetryAttempt(0)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-100 mb-6">
        Generate New Image
      </h3>
      
      <form 
        onSubmit={(e) => {
          console.log('Form onSubmit triggered - prompt:', `"${prompt}"`, 'selectedFile:', selectedFile)
          handleSubmit(e)
        }} 
        className="space-y-4" 
        noValidate
      >
        {/* Reference Image Upload */}
        <div>
          {!previewUrl ? (
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer ${
                dragActive 
                  ? 'border-teal-500 bg-[#1a2332]/80' 
                  : 'border-[#2a3441] hover:border-teal-500/50 hover:bg-[#1a2332]/40'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-500 mb-3" />
              <p className="text-sm text-gray-300 mb-1">
                Click to upload a reference image
              </p>
              <p className="text-xs text-gray-500">
                PNG, JPG, GIF up to 10MB
              </p>
              {dragActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 animate-pulse"></div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInputChange}
                className="hidden"
              />
            </div>
          ) : (
            /* Preview Area */
            <div className="relative group">
              <div className="rounded-lg overflow-hidden border border-[#2a3441]">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="w-full h-auto max-h-96 object-contain"
                />
              </div>
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 bg-red-500/90 hover:bg-red-600 text-white rounded-full p-1.5 transition-colors shadow-lg"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>

        {/* Prompt Input */}
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
            Describe how you want to use the reference image
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Use this image as inspiration, change the style to watercolor, add a sunset background..."
            className="input-field min-h-[120px] resize-none"
            disabled={isGenerating}
            rows={4}
          />
          <div className="flex justify-between items-center mt-1">
            <span className={`text-xs ${prompt.length > 1000 ? 'text-red-400' : 'text-gray-500'}`}>
              {prompt.length}/1000 characters
            </span>
            {prompt.length > 1000 && (
              <span className="text-xs text-red-400">
                Prompt too long!
              </span>
            )}
          </div>
        </div>

        {error && (
          <div className="text-red-300 text-sm bg-red-900/20 border border-red-500/30 rounded-lg p-3">
            {error}
          </div>
        )}

        {/* Retry Progress */}
        {isGenerating && retryAttempt > 0 && (
          <div className="text-teal-300 text-sm bg-teal-900/20 border border-teal-500/30 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-teal-400 border-t-transparent"></div>
              <span>Retrying... Attempt {retryAttempt} of {maxRetries}</span>
            </div>
            <div className="w-full bg-teal-900/30 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-teal-500 to-cyan-600 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${(retryAttempt / maxRetries) * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={isGenerating || !prompt.trim() || !selectedFile || prompt.length > 1000}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          onClick={(e) => {
            console.log('Button clicked - prompt:', `"${prompt}"`, 'length:', prompt.length, 'selectedFile:', selectedFile, 'disabled:', isGenerating || !prompt.trim() || !selectedFile || prompt.length > 1000)
          }}
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              <span>
                {retryAttempt > 0 ? `Retrying... (${retryAttempt}/${maxRetries})` : 'Generating...'}
              </span>
            </>
          ) : (
            <>
              <SparklesIcon className="h-4 w-4" />
              <span>Generate Image</span>
            </>
          )}
        </button>
      </form>

    </div>
  )
}
