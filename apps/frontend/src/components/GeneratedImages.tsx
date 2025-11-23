'use client'

import { useState } from 'react'
import Image from 'next/image'
import { PhotoIcon, ArrowDownTrayIcon, BookmarkIcon, CheckIcon, TrashIcon } from '@heroicons/react/24/outline'
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
  onDelete?: (imageId: string | number) => void
}

export default function GeneratedImages({ images, onDelete }: GeneratedImagesProps) {
  const { addToast } = useToast()
  const [savingIds, setSavingIds] = useState<Set<string | number>>(new Set())
  const [savedIds, setSavedIds] = useState<Set<string | number>>(new Set())

  const handleDownload = (image: ImageData) => {
    try {
      // Create a temporary link to download the image
      const link = document.createElement('a')
      link.href = image.imageUrl || image.modifiedImageUrl || '/placeholder-image.jpg'
      // Use the image's creation timestamp for consistent naming
      const timestamp = new Date(image.createdAt).getTime()
      link.download = `image-${timestamp}.png`
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleDownloadAll = async () => {
    if (images.length === 0) return

    try {
      // Download each image with a small delay to avoid browser blocking
      for (let i = 0; i < images.length; i++) {
        const image = images[i]
        const imageUrl = image.imageUrl || image.modifiedImageUrl
        
        if (!imageUrl || imageUrl === '/placeholder-image.jpg') {
          continue
        }

        // Fetch the image as a blob
        const response = await fetch(imageUrl)
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        
        // Create download link
        const link = document.createElement('a')
        link.href = url
        const timestamp = new Date(image.createdAt).getTime()
        link.download = `image-${timestamp}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Clean up the blob URL
        window.URL.revokeObjectURL(url)
        
        // Small delay between downloads to avoid browser blocking
        if (i < images.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 300))
        }
      }

      addToast({
        type: 'success',
        title: 'Download Started',
        message: `Downloading ${images.length} image(s)...`,
        duration: 3000
      })
    } catch (error) {
      console.error('Download all failed:', error)
      addToast({
        type: 'error',
        title: 'Download Failed',
        message: 'Failed to download all images. Please try again.',
        duration: 4000
      })
    }
  }

  const handleDelete = (image: ImageData) => {
    if (onDelete) {
      onDelete(image.id)
      addToast({
        type: 'success',
        title: 'Image Deleted',
        message: 'The image has been removed from your collection',
        duration: 2000
      })
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
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Created Images ({images.length})
        </h3>
        {images.length > 0 && (
          <button
            onClick={handleDownloadAll}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-primary-600 to-blue-600 text-white text-sm font-medium rounded-md hover:from-primary-700 hover:to-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            title="Download all images"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            <span>Download All</span>
          </button>
        )}
      </div>
      
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
                      {onDelete && (
                        <button
                          onClick={() => handleDelete(image)}
                          className="p-1 rounded-full bg-red-500/80 hover:bg-red-600/80 transition-colors"
                          title="Delete Image"
                        >
                          <TrashIcon className="h-4 w-4 text-white" />
                        </button>
                      )}
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
                {onDelete && (
                  <button
                    onClick={() => handleDelete(image)}
                    className="p-1.5 rounded-full bg-red-500/90 hover:bg-red-600 transition-colors shadow-sm"
                    title="Delete Image"
                  >
                    <TrashIcon className="h-4 w-4 text-white" />
                  </button>
                )}
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
