'use client'

import { useState } from 'react'
import Image from 'next/image'
import { PhotoIcon, ArrowDownTrayIcon, HeartIcon } from '@heroicons/react/24/outline'

interface ImageData {
  id: string | number
  prompt: string
  imageUrl?: string
  originalImageUrl?: string
  modifiedImageUrl?: string
  referenceImageUrl?: string
  status: string
  createdAt: string
  type?: 'generation' | 'modification'
}

interface GeneratedImagesProps {
  images: ImageData[]
}

export default function GeneratedImages({ images }: GeneratedImagesProps) {
  const [selectedImage, setSelectedImage] = useState<ImageData | null>(null)

  const handleDownload = (image: ImageData) => {
    // Create a temporary link to download the image
    const link = document.createElement('a')
    link.href = image.imageUrl
    link.download = `generated-image-${image.id}.jpg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleLike = (imageId: number) => {
    // TODO: Implement like functionality
    console.log('Liked image:', imageId)
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
            <div className="aspect-square relative">
              <Image
                src={image.modifiedImageUrl || image.imageUrl || '/placeholder-image.jpg'}
                alt={image.prompt}
                fill
                className="object-cover"
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
                        onClick={() => handleLike(image.id)}
                        className="p-1 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                        title="Like"
                      >
                        <HeartIcon className="h-4 w-4 text-white" />
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

              {/* Status badge */}
              <div className="absolute top-2 right-2">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  image.status === 'completed' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {image.type === 'modification' ? 'Modified' : 'Generated'}
                </span>
              </div>
            </div>
            
            {/* Reference Image */}
            {image.referenceImageUrl && (
              <div className="mt-2">
                <div className="text-xs text-gray-500 mb-1">Reference Image:</div>
                <div className="relative w-full h-20 rounded overflow-hidden">
                  <Image
                    src={image.referenceImageUrl}
                    alt="Reference"
                    fill
                    className="object-cover"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder-image.jpg'
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
