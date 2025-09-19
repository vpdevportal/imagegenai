'use client'

import { useState, useRef, useEffect } from 'react'
import { SparklesIcon, PhotoIcon, ArrowUpTrayIcon, XMarkIcon } from '@heroicons/react/24/outline'
import Image from 'next/image'
import { generateImage } from '@/lib/api'

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

    if (!selectedFile) {
      console.log('Validation failed: No file selected')
      setError('Please select a reference image')
      return
    }

    setError('')
    setIsGenerating(true)

    try {
      console.log('Calling generateImage API with prompt:', `"${prompt}"`, 'file:', selectedFile.name)
      const response = await generateImage(prompt, selectedFile)
      
      onImageGenerated({
        id: response.id,
        prompt,
        imageUrl: response.generated_image_url || '/placeholder-image.jpg',
        referenceImageUrl: response.reference_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: 'generation-with-reference'
      })
    } catch (err) {
      setError('Failed to generate image. Please try again.')
      console.error('Image generation error:', err)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
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
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
                dragActive 
                  ? 'border-primary-500 bg-primary-50' 
                  : 'border-gray-300 hover:border-primary-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-gray-600 mb-2">
                Click to upload a reference image
              </p>
              <p className="text-xs text-gray-500">
                PNG, JPG, GIF up to 10MB
              </p>
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
            <div className="relative">
              <img
                src={previewUrl}
                alt="Preview"
                className="w-full h-48 object-cover rounded-lg"
              />
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
        </div>

        {/* Prompt Input */}
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
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
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isGenerating || !prompt.trim() || !selectedFile}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          onClick={(e) => {
            console.log('Button clicked - prompt:', `"${prompt}"`, 'selectedFile:', selectedFile, 'disabled:', isGenerating || !prompt.trim() || !selectedFile)
          }}
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating...</span>
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
