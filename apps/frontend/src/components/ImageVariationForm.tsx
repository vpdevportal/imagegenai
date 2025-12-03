'use client'

import { useState, useRef } from 'react'
import { SparklesIcon, PhotoIcon, ArrowUpTrayIcon, XMarkIcon } from '@heroicons/react/24/outline'
import Image from 'next/image'
import { generateVariation } from '@/services/api'
import { useProvider } from '@/contexts/ProviderContext'

interface ImageVariationFormProps {
  onVariationGenerated: (variation: any) => void
  isGenerating: boolean
  setIsGenerating: (value: boolean) => void
}

export default function ImageVariationForm({ 
  onVariationGenerated, 
  isGenerating, 
  setIsGenerating
}: ImageVariationFormProps) {
  const { provider } = useProvider()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [prompt, setPrompt] = useState('')
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setSelectedFile(file)
    setError('')

    // Create preview URL
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
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
    
    setError('')
    
    if (!selectedFile) {
      setError('Please select an image file')
      return
    }

    if (prompt.length > 1000) {
      setError('Prompt too long (max 1000 characters)')
      return
    }

    setIsGenerating(true)

    try {
      const response = await generateVariation(selectedFile, prompt || undefined, provider)
      
      onVariationGenerated({
        id: response.id,
        prompt: response.original_prompt || 'Automatic variation',
        imageUrl: response.generated_image_url,
        referenceImageUrl: response.reference_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: 'variation'
      })
    } catch (err: any) {
      console.error('Image variation error:', err)
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to generate image variation. Please try again.'
      setError(errorMessage)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-100 mb-6">
        Generate Image Variation
      </h3>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload Area */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Upload Image
          </label>
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => !isGenerating && fileInputRef.current?.click()}
            className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 ${
              dragActive
                ? 'border-teal-500 bg-[#1a2332]/80'
                : 'border-[#2a3441] hover:border-teal-500/50 hover:bg-[#1a2332]/40'
            } ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {previewUrl ? (
              <div className="relative w-full h-48 mb-4">
                <Image
                  src={previewUrl}
                  alt="Preview"
                  fill
                  className="object-contain rounded-lg"
                />
                {!isGenerating && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      clearImage()
                    }}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                )}
              </div>
            ) : (
              <>
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-500 mb-3" />
                <p className="text-sm font-semibold text-gray-300 mb-2">
                  Click to upload or drag and drop
                </p>
                <p className="text-xs text-gray-400">
                  PNG, JPG, GIF up to 10MB
                </p>
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  handleFileSelect(file)
                }
              }}
              disabled={isGenerating}
              className="hidden"
            />
          </div>
        </div>

        {/* Optional Prompt Field */}
        <div>
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Variation Description <span className="text-gray-500 font-normal">(Optional)</span>
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the variation you want (e.g., 'change background to sunset', 'make it more colorful'). Leave empty for automatic variation."
            disabled={isGenerating}
            rows={4}
            maxLength={1000}
            className="input-field resize-none"
          />
          <div className="flex justify-between items-center mt-1">
            <p className="text-xs text-gray-400">
              Leave empty for automatic variation generation
            </p>
            <span className="text-xs text-gray-400">
              {prompt.length}/1000
            </span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!selectedFile || isGenerating}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Variation...
            </>
          ) : (
            <>
              <SparklesIcon className="h-5 w-5 mr-2" />
              Generate Variation
            </>
          )}
        </button>
      </form>
    </div>
  )
}

