'use client'

import { useState, Suspense } from 'react'
import ImageGroupingForm from '@/components/ImageGroupingForm'
import GeneratedImages from '@/components/GeneratedImages'

export default function GroupingPage() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleImageGenerated = (newImage: any) => {
    setImages(prev => [newImage, ...prev])
  }

  const handleDeleteImage = (imageId: string | number) => {
    setImages(prev => prev.filter(img => img.id !== imageId))
  }

  return (
    <Suspense fallback={<div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div></div>}>
      <div className="py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Image Grouping Form */}
            <div className="order-1 lg:order-1">
              <ImageGroupingForm 
                onImageGenerated={handleImageGenerated}
                isGenerating={isGenerating}
                setIsGenerating={setIsGenerating}
              />
            </div>
            
            {/* Generated Images */}
            <div className="order-2 lg:order-2">
              <GeneratedImages images={images} onDelete={handleDeleteImage} />
            </div>
          </div>
        </div>
      </div>
    </Suspense>
  )
}

