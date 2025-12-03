'use client'

import { useState, useRef } from 'react'
import { GlobeAmericasIcon, PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline'
import Image from 'next/image'
import { generateTeleport } from '@/services/api'
import { useProvider } from '@/contexts/ProviderContext'

interface ImageTeleportFormProps {
  onTeleportGenerated: (result: any) => void
  isGenerating: boolean
  setIsGenerating: (value: boolean) => void
}

export default function ImageTeleportForm({
  onTeleportGenerated,
  isGenerating,
  setIsGenerating
}: ImageTeleportFormProps) {
  const { provider } = useProvider()
  const [backgroundFile, setBackgroundFile] = useState<File | null>(null)
  const [personFile, setPersonFile] = useState<File | null>(null)
  const [backgroundPreview, setBackgroundPreview] = useState<string | null>(null)
  const [personPreview, setPersonPreview] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [dragActiveBg, setDragActiveBg] = useState(false)
  const [dragActivePerson, setDragActivePerson] = useState(false)
  const bgInputRef = useRef<HTMLInputElement>(null)
  const personInputRef = useRef<HTMLInputElement>(null)

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

  const clearImage = (type: 'background' | 'person') => {
    if (type === 'background') {
      setBackgroundFile(null)
      if (backgroundPreview) {
        URL.revokeObjectURL(backgroundPreview)
        setBackgroundPreview(null)
      }
    } else {
      setPersonFile(null)
      if (personPreview) {
        URL.revokeObjectURL(personPreview)
        setPersonPreview(null)
      }
    }
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation()

    setError('')

    if (!personFile) {
      setError('Please select a person image')
      return
    }

    if (!backgroundFile) {
      setError('Please select a background image')
      return
    }

    setIsGenerating(true)

    try {
      const response = await generateTeleport(personFile, backgroundFile, provider)

      onTeleportGenerated({
        id: response.id,
        prompt: response.prompt || 'Teleport person to new background',
        imageUrl: response.generated_image_url,
        referenceImageUrl: response.reference_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: 'teleport'
      })
    } catch (err: any) {
      console.error('Teleport error:', err)
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to generate teleport image. Please try again.'
      setError(errorMessage)
    } finally {
      setIsGenerating(false)
    }
  }

  const renderUploadArea = (
    type: 'background' | 'person',
    selectedFile: File | null,
    previewUrl: string | null,
    dragActive: boolean,
    setDragActive: (active: boolean) => void,
    fileInputRef: React.RefObject<HTMLInputElement>,
    label: string,
    description: string
  ) => {
    return (
      <div>
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          {label}
        </label>
        <div
          onDragEnter={(e) => handleDrag(e, setDragActive)}
          onDragLeave={(e) => handleDrag(e, setDragActive)}
          onDragOver={(e) => handleDrag(e, setDragActive)}
          onDrop={(e) => {
            if (type === 'background') {
              handleDrop(e, setBackgroundFile, setBackgroundPreview, backgroundPreview, setDragActiveBg)
            } else {
              handleDrop(e, setPersonFile, setPersonPreview, personPreview, setDragActivePerson)
            }
          }}
          onClick={() => !isGenerating && fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 ${dragActive
              ? 'border-teal-500 bg-[#1a2332]/80'
              : 'border-[#2a3441] hover:border-teal-500/50 hover:bg-[#1a2332]/40'
            } ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          {previewUrl ? (
            <div className="relative w-full h-48 mb-4">
              <Image
                src={previewUrl}
                alt={`${type} preview`}
                fill
                className="object-contain rounded-lg"
              />
              {!isGenerating && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    clearImage(type)
                  }}
                  className="absolute top-2 right-2 p-2 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-full hover:from-red-600 hover:to-pink-700 transition-all duration-300 shadow-lg"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              )}
            </div>
          ) : (
            <>
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-500 mb-3" />
              <p className="text-sm font-semibold text-gray-300 mb-2">
                {description}
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
                if (type === 'background') {
                  handleFileSelect(file, setBackgroundFile, setBackgroundPreview, backgroundPreview)
                } else {
                  handleFileSelect(file, setPersonFile, setPersonPreview, personPreview)
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
      <h3 className="text-lg font-semibold text-gray-100 mb-6">
        Replace Person&apos;s Background
      </h3>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Person Image Upload */}
        {renderUploadArea(
          'person',
          personFile,
          personPreview,
          dragActivePerson,
          setDragActivePerson,
          personInputRef,
          '1. Person Image',
          'Upload the image containing the person (this will be the primary image)'
        )}

        {/* Background Image Upload */}
        {renderUploadArea(
          'background',
          backgroundFile,
          backgroundPreview,
          dragActiveBg,
          setDragActiveBg,
          bgInputRef,
          '2. Background Scene',
          'Upload the background image to replace the person\'s current background'
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!personFile || !backgroundFile || isGenerating}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Teleporting...
            </>
          ) : (
            <>
              <GlobeAmericasIcon className="h-5 w-5 mr-2" />
              Teleport Person
            </>
          )}
        </button>
      </form>
    </div>
  )
}
