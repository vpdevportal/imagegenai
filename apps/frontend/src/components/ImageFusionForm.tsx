'use client'

import { useState, useRef } from 'react'
import { ArrowsRightLeftIcon, PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline'
import Image from 'next/image'
import { generateFusion } from '@/lib/api'

interface ImageFusionFormProps {
  onFusionGenerated: (fusion: any) => void
  isGenerating: boolean
  setIsGenerating: (value: boolean) => void
}

export default function ImageFusionForm({ 
  onFusionGenerated, 
  isGenerating, 
  setIsGenerating
}: ImageFusionFormProps) {
  const [selectedFile1, setSelectedFile1] = useState<File | null>(null)
  const [selectedFile2, setSelectedFile2] = useState<File | null>(null)
  const [previewUrl1, setPreviewUrl1] = useState<string | null>(null)
  const [previewUrl2, setPreviewUrl2] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [dragActive1, setDragActive1] = useState(false)
  const [dragActive2, setDragActive2] = useState(false)
  const fileInputRef1 = useRef<HTMLInputElement>(null)
  const fileInputRef2 = useRef<HTMLInputElement>(null)

  const handleFileSelect = (file: File, setFile: (f: File | null) => void, setPreview: (url: string | null) => void, preview: string | null) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setFile(file)
    setError('')

    // Create preview URL
    if (preview) {
      URL.revokeObjectURL(preview)
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
  }

  const handleDrag = (e: React.DragEvent, setDragActive: (active: boolean) => void) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent, setFile: (f: File | null) => void, setPreview: (url: string | null) => void, preview: string | null, setDragActive: (active: boolean) => void) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleFileSelect(file, setFile, setPreview, preview)
    }
  }

  const clearImage = (imageNum: 1 | 2) => {
    if (imageNum === 1) {
      setSelectedFile1(null)
      if (previewUrl1) {
        URL.revokeObjectURL(previewUrl1)
        setPreviewUrl1(null)
      }
    } else {
      setSelectedFile2(null)
      if (previewUrl2) {
        URL.revokeObjectURL(previewUrl2)
        setPreviewUrl2(null)
      }
    }
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    setError('')
    
    if (!selectedFile1) {
      setError('Please select the first image')
      return
    }

    if (!selectedFile2) {
      setError('Please select the second image')
      return
    }

    setIsGenerating(true)

    try {
      const response = await generateFusion(selectedFile1, selectedFile2)
      
      onFusionGenerated({
        id: response.id,
        prompt: response.prompt || 'Fusion of two people',
        imageUrl: response.generated_image_url,
        referenceImageUrl: response.reference_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: 'fusion'
      })
    } catch (err: any) {
      console.error('Image fusion error:', err)
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to generate image fusion. Please try again.'
      setError(errorMessage)
    } finally {
      setIsGenerating(false)
    }
  }

  const renderUploadArea = (
    imageNum: 1 | 2,
    selectedFile: File | null,
    previewUrl: string | null,
    dragActive: boolean,
    setDragActive: (active: boolean) => void,
    fileInputRef: React.RefObject<HTMLInputElement>
  ) => {
    return (
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Person {imageNum} Image
        </label>
        <div
          onDragEnter={(e) => handleDrag(e, setDragActive)}
          onDragLeave={(e) => handleDrag(e, setDragActive)}
          onDragOver={(e) => handleDrag(e, setDragActive)}
          onDrop={(e) => {
            if (imageNum === 1) {
              handleDrop(e, setSelectedFile1, setPreviewUrl1, previewUrl1, setDragActive1)
            } else {
              handleDrop(e, setSelectedFile2, setPreviewUrl2, previewUrl2, setDragActive2)
            }
          }}
          onClick={() => !isGenerating && fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            dragActive
              ? 'border-purple-500 bg-purple-50'
              : 'border-gray-300 hover:border-purple-400'
          } ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          {previewUrl ? (
            <div className="relative w-full h-48 mb-4">
              <Image
                src={previewUrl}
                alt={`Preview ${imageNum}`}
                fill
                className="object-contain rounded-lg"
              />
              {!isGenerating && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    clearImage(imageNum)
                  }}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              )}
            </div>
          ) : (
            <>
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-gray-600 mb-2">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-gray-500">
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
                if (imageNum === 1) {
                  handleFileSelect(file, setSelectedFile1, setPreviewUrl1, previewUrl1)
                } else {
                  handleFileSelect(file, setSelectedFile2, setPreviewUrl2, previewUrl2)
                }
              }
            }}
            disabled={isGenerating}
            className="hidden"
          />
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
        <ArrowsRightLeftIcon className="h-5 w-5 mr-2 text-purple-600" />
        Fuse Two People Together
      </h3>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* First Image Upload */}
        {renderUploadArea(1, selectedFile1, previewUrl1, dragActive1, setDragActive1, fileInputRef1)}

        {/* Second Image Upload */}
        {renderUploadArea(2, selectedFile2, previewUrl2, dragActive2, setDragActive2, fileInputRef2)}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!selectedFile1 || !selectedFile2 || isGenerating}
          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-4 rounded-md hover:from-purple-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Fusion...
            </>
          ) : (
            <>
              <ArrowsRightLeftIcon className="h-5 w-5 mr-2" />
              Generate Fusion
            </>
          )}
        </button>
      </form>
    </div>
  )
}

