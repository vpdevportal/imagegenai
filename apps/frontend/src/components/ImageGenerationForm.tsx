'use client'

import { useState, useRef } from 'react'
import { SparklesIcon, PhotoIcon, ArrowUpTrayIcon, XMarkIcon } from '@heroicons/react/24/outline'
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
    
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setError('')
    setIsGenerating(true)

    try {
      const response = await generateImage(prompt, selectedFile || undefined)
      onImageGenerated({
        id: response.id,
        prompt,
        imageUrl: response.generated_image_url || '/placeholder-image.jpg',
        referenceImageUrl: response.reference_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: selectedFile ? 'generation-with-reference' : 'generation'
      })
      setPrompt('')
      clearImage()
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
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Optional Reference Image Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Reference Image (Optional)
          </label>
          
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
              <p className="text-sm text-gray-600 mb-2">
                Drag and drop a reference image, or click to select
              </p>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="btn-secondary text-sm"
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
            <div className="relative">
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={previewUrl}
                  alt="Reference preview"
                  className="w-full h-full object-cover"
                />
              </div>
              <button
                type="button"
                onClick={clearImage}
                className="absolute top-2 right-2 p-1 bg-black bg-opacity-50 text-white rounded-full hover:bg-opacity-70"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>

        {/* Prompt Input */}
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
            {selectedFile ? 'Describe how you want to use the reference image' : 'Describe the image you want to generate'}
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={selectedFile 
              ? "Use this image as inspiration, change the style to watercolor, add a sunset background..."
              : "A serene mountain landscape at sunset with a lake reflecting the sky..."
            }
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
          disabled={isGenerating || !prompt.trim()}
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

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-2">
          {selectedFile ? 'Tips for reference image generation:' : 'Tips for better results:'}
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          {selectedFile ? (
            <>
              <li>• Describe how you want to use the reference image</li>
              <li>• Specify style changes (watercolor, oil painting, digital art)</li>
              <li>• Mention composition changes or additions</li>
              <li>• Try prompts like "make it more vibrant" or "add vintage effects"</li>
            </>
          ) : (
            <>
              <li>• Be descriptive and specific</li>
              <li>• Include style preferences (photorealistic, artistic, etc.)</li>
              <li>• Mention lighting and mood</li>
              <li>• Add details about composition</li>
            </>
          )}
        </ul>
      </div>
    </div>
  )
}
