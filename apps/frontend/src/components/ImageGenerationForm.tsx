'use client'

import { useState, useRef } from 'react'
import { SparklesIcon, PhotoIcon, ArrowUpTrayIcon, XMarkIcon } from '@heroicons/react/24/outline'
import Image from 'next/image'
import { generateImage } from '@/lib/api'

interface ImageGenerationFormProps {
  onImageGenerated: (image: any) => void
  isGenerating: boolean
  setIsGenerating: (value: boolean) => void
}

export default function ImageGenerationForm({ 
  onImageGenerated, 
  isGenerating, 
  setIsGenerating 
}: ImageGenerationFormProps) {
  const [prompt, setPrompt] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

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
    
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    if (!selectedFile) {
      setError('Please select a reference image')
      return
    }

    setError('')
    setIsGenerating(true)

    try {
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
      
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        {/* Optional Reference Image Upload */}
        <div>
          
          {!previewUrl ? (
            <div
              className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                dragActive 
                  ? 'border-primary-500 bg-primary-50' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <PhotoIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600 mb-3">
                Drag and drop a reference image, or click to select
                <br />
                <span className="text-red-500 text-xs">Reference image is required</span>
              </p>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
              >
                <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
                Choose Image
              </button>
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
            <div className="relative group bg-gray-100 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square relative">
                <Image
                  src={previewUrl}
                  alt="Reference preview"
                  fill
                  className="object-cover"
                  onError={(e) => {
                    e.currentTarget.src = '/placeholder-image.jpg'
                  }}
                />
                
                {/* Overlay with remove button */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200">
                  <div className="absolute top-2 right-2">
                    <button
                      type="button"
                      onClick={clearImage}
                      className="p-1.5 rounded-full bg-white/90 hover:bg-white transition-colors shadow-sm"
                      title="Remove Image"
                    >
                      <XMarkIcon className="h-4 w-4 text-gray-700" />
                    </button>
                  </div>
                </div>
              </div>
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
