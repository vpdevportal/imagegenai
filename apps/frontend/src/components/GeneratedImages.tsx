'use client'

import { useState } from 'react'
import Image from 'next/image'
import { PhotoIcon, ArrowDownTrayIcon, BookmarkIcon, CheckIcon, TrashIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { savePrompt, normalizeImageUrl } from '@/services/api'
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
  onClearAll?: () => void
}

export default function GeneratedImages({ images, onDelete, onClearAll }: GeneratedImagesProps) {
  const { addToast } = useToast()
  const [savingIds, setSavingIds] = useState<Set<string | number>>(new Set())
  const [savedIds, setSavedIds] = useState<Set<string | number>>(new Set())
  const [hoveredImageId, setHoveredImageId] = useState<string | number | null>(null)

  const handleDownload = (image: ImageData) => {
    try {
      // Normalize the image URL to avoid local network permission issues
      const imageUrl = normalizeImageUrl(image.imageUrl || image.modifiedImageUrl)
      
      // Create a temporary link to download the image
      const link = document.createElement('a')
      link.href = imageUrl
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
        const imageUrl = normalizeImageUrl(image.imageUrl || image.modifiedImageUrl)
        
        if (!imageUrl || imageUrl === '/placeholder-image.jpg') {
          continue
        }

        // Fetch the image as a blob - normalized URL ensures it goes through Next.js proxy
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
          <PhotoIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-300 mb-2">
            No images created yet
          </h3>
          <p className="text-gray-500 text-sm">
            Generate new images or modify existing ones using the form on the left
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-100">
          Created Images ({images.length})
        </h3>
        {images.length > 0 && (
          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownloadAll}
              className="btn-secondary flex items-center space-x-2 text-sm"
              title="Download all images"
            >
              <ArrowDownTrayIcon className="h-4 w-4" />
              <span>Download All</span>
            </button>
            {onClearAll && (
              <button
                onClick={onClearAll}
                className="btn-secondary flex items-center space-x-2 text-sm text-red-300 hover:text-red-200 border-red-500/40 hover:border-red-500/60"
                title="Clear all images"
              >
                <XMarkIcon className="h-4 w-4" />
                <span>Clear</span>
              </button>
            )}
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 gap-4 max-h-[600px] overflow-y-auto">
        {images.map((image) => (
          <div
            key={image.id}
            className="relative group bg-[#1a2332]/40 rounded-lg overflow-hidden border border-[#2a3441] hover:border-teal-500/30 transition-all duration-200"
            onMouseEnter={() => setHoveredImageId(image.id)}
            onMouseLeave={() => setHoveredImageId(null)}
          >
            {/* Generated Image */}
            <div className="relative w-full bg-[#0a1929]" style={{ minHeight: '300px' }}>
              <Image
                src={normalizeImageUrl(image.modifiedImageUrl || image.imageUrl) || '/placeholder-image.jpg'}
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
              <div className={`absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent transition-all duration-300 ${
                hoveredImageId === image.id ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
              }`}>
                <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 via-black/60 to-transparent pointer-events-auto">
                  <p className="text-white text-sm font-medium mb-3 line-clamp-2 drop-shadow-lg">
                    {image.prompt}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-200 font-medium">
                      {new Date(image.createdAt).toLocaleDateString()}
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSavePrompt(image)}
                        disabled={savingIds.has(image.id) || savedIds.has(image.id)}
                        className="p-2 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-110 active:scale-95 shadow-lg z-10"
                        title={savedIds.has(image.id) ? 'Saved' : 'Save Prompt'}
                      >
                        {savingIds.has(image.id) ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                        ) : savedIds.has(image.id) ? (
                          <CheckIcon className="h-4 w-4 text-white" />
                        ) : (
                          <BookmarkIcon className="h-4 w-4 text-white" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDownload(image)}
                        className="p-2 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all duration-300 transform hover:scale-110 active:scale-95 shadow-lg z-10"
                        title="Download"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4 text-white" />
                      </button>
                      {onDelete && (
                        <button
                          onClick={() => handleDelete(image)}
                          className="p-2 rounded-xl bg-gradient-to-r from-red-500/80 to-pink-600/80 hover:from-red-600 hover:to-pink-700 backdrop-blur-sm transition-all duration-300 transform hover:scale-110 active:scale-95 shadow-lg z-10"
                          title="Delete Image"
                        >
                          <TrashIcon className="h-4 w-4 text-white" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Status badge and action buttons - show on hover (same as bottom overlay), hide when mouse leaves */}
              <div className={`absolute top-4 right-4 flex items-center space-x-2 transition-opacity duration-300 pointer-events-auto z-20 ${
                hoveredImageId === image.id ? 'opacity-100' : 'opacity-0'
              }`}>
                <button
                  onClick={() => handleSavePrompt(image)}
                  disabled={savingIds.has(image.id) || savedIds.has(image.id)}
                  className="p-2 rounded-xl bg-gray-800/95 backdrop-blur-sm hover:bg-gray-700 transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-110 active:scale-95"
                  title={savedIds.has(image.id) ? 'Saved' : 'Save Prompt'}
                >
                  {savingIds.has(image.id) ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-indigo-400 border-t-transparent"></div>
                  ) : savedIds.has(image.id) ? (
                    <CheckIcon className="h-4 w-4 text-green-400" />
                  ) : (
                    <BookmarkIcon className="h-4 w-4 text-indigo-400" />
                  )}
                </button>
                <button
                  onClick={() => handleDownload(image)}
                  className="p-2 rounded-xl bg-gray-800/95 backdrop-blur-sm hover:bg-gray-700 transition-all duration-300 shadow-lg transform hover:scale-110 active:scale-95"
                  title="Download Image"
                >
                  <ArrowDownTrayIcon className="h-4 w-4 text-indigo-400" />
                </button>
                {onDelete && (
                  <button
                    onClick={() => handleDelete(image)}
                    className="p-2 rounded-xl bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 transition-all duration-300 shadow-lg transform hover:scale-110 active:scale-95"
                    title="Delete Image"
                  >
                    <TrashIcon className="h-4 w-4 text-white" />
                  </button>
                )}
                <span className={`px-3 py-1.5 text-xs font-semibold rounded-full shadow-md backdrop-blur-sm ${
                  image.status === 'completed' 
                    ? 'bg-gradient-to-r from-green-900/80 to-emerald-900/80 text-green-300 border border-green-700/50' 
                    : 'bg-gradient-to-r from-yellow-900/80 to-amber-900/80 text-yellow-300 border border-yellow-700/50'
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
