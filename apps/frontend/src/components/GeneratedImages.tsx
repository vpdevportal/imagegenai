'use client'

import { useState } from 'react'
import Image from 'next/image'
import { PhotoIcon, ArrowDownTrayIcon, BookmarkIcon, CheckIcon } from '@heroicons/react/24/outline'
import { savePrompt } from '@/lib/api'
import { useToast } from '@/contexts/ToastContext'

interface ImageData {
  id: string | number
  prompt: string
  imageUrl?: string
  modifiedImageUrl?: string
  status: string
  createdAt: string
  type?: 'generation' | 'modification'
}

interface GeneratedImagesProps {
  images: ImageData[]
}

export default function GeneratedImages({ images }: GeneratedImagesProps) {
  const { addToast } = useToast()
  const [savingIds, setSavingIds] = useState<Set<string | number>>(new Set())
  const [savedIds, setSavedIds] = useState<Set<string | number>>(new Set())

  const handleDownload = (image: ImageData) => {
    try {
      // Create a temporary link to download the image
      const link = document.createElement('a')
      link.href = image.imageUrl || image.modifiedImageUrl || '/placeholder-image.jpg'
      const timestamp = Math.floor(Date.now() / 1000) // Current time in seconds from epoch
      link.download = `image-${timestamp}.png`
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleSavePrompt = async (image: ImageData) => {
    if (savedIds.has(image.id) || savingIds.has(image.id)) {
      return
    }

    setSavingIds(prev => new Set(prev).add(image.id))

    try {
      await savePrompt(image.prompt)
      
      setSavedIds(prev => new Set(prev).add(image.id))
      addToast({
        type: 'success',
        title: 'Prompt Saved',
        message: 'The prompt has been saved to your collection',
        duration: 3000
      })
    } catch (error: any) {
      console.error('Failed to save prompt:', error)
      addToast({
        type: 'error',
        title: 'Save Failed',
        message: error?.response?.data?.detail || 'Failed to save prompt. Please try again.',
        duration: 4000
      })
    } finally {
      setSavingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(image.id)
        return newSet
      })
    }
  }


  if (images.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <PhotoIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No images created yet
          </h3>
          <p className="text-gray-500">
            Generate new images or modify existing ones using the form on the left
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Created Images ({images.length})
      </h3>
      
      <div className="grid grid-cols-1 gap-4 max-h-[600px] overflow-y-auto">
        {images.map((image) => (
          <div
            key={image.id}
            className="relative group bg-gray-100 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
          >
            {/* Generated Image */}
            <div className="relative w-full" style={{ minHeight: '300px' }}>
              <Image
                src={image.modifiedImageUrl || image.imageUrl || '/placeholder-image.jpg'}
                alt={image.prompt}
                width={800}
                height={800}
                className="object-contain w-full h-auto"
                onError={(e) => {
                  // Fallback to placeholder if image fails to load
                  e.currentTarget.src = '/placeholder-image.jpg'
                }}
              />
              
              {/* Overlay with actions */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200">
                <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <p className="text-white text-sm mb-2 line-clamp-2">
                    {image.prompt}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-200">
                      {new Date(image.createdAt).toLocaleDateString()}
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSavePrompt(image)}
                        disabled={savingIds.has(image.id) || savedIds.has(image.id)}
                        className="p-1 rounded-full bg-white/20 hover:bg-white/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title={savedIds.has(image.id) ? 'Saved' : 'Save Prompt'}
                      >
                        {savingIds.has(image.id) ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : savedIds.has(image.id) ? (
                          <CheckIcon className="h-4 w-4 text-white" />
                        ) : (
                          <BookmarkIcon className="h-4 w-4 text-white" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDownload(image)}
                        className="p-1 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                        title="Download"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4 text-white" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Status badge and action buttons */}
              <div className="absolute top-2 right-2 flex items-center space-x-2">
                <button
                  onClick={() => handleSavePrompt(image)}
                  disabled={savingIds.has(image.id) || savedIds.has(image.id)}
                  className="p-1.5 rounded-full bg-white/90 hover:bg-white transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  title={savedIds.has(image.id) ? 'Saved' : 'Save Prompt'}
                >
                  {savingIds.has(image.id) ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700"></div>
                  ) : savedIds.has(image.id) ? (
                    <CheckIcon className="h-4 w-4 text-green-600" />
                  ) : (
                    <BookmarkIcon className="h-4 w-4 text-gray-700" />
                  )}
                </button>
                <button
                  onClick={() => handleDownload(image)}
                  className="p-1.5 rounded-full bg-white/90 hover:bg-white transition-colors shadow-sm"
                  title="Download Image"
                >
                  <ArrowDownTrayIcon className="h-4 w-4 text-gray-700" />
                </button>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  image.status === 'completed' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {image.type === 'modification' ? 'Modified' : 'Generated'}
                </span>
              </div>
            </div>
            
          </div>
        ))}
      </div>
    </div>
  )
}
