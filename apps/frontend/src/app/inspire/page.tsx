'use client'

import { useState } from 'react'
import ImageGenerationForm from '@/components/ImageGenerationForm'
import GeneratedImages from '@/components/GeneratedImages'

export default function InspirePage() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleImageGenerated = (newImage: any) => {
    setImages(prev => [newImage, ...prev])
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Get Inspired</h1>
          <p className="text-lg text-gray-600">Discover creative possibilities with AI-powered image generation</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image Generation Form */}
          <div className="order-2 lg:order-1">
            <ImageGenerationForm 
              onImageGenerated={handleImageGenerated}
              isGenerating={isGenerating}
              setIsGenerating={setIsGenerating}
            />
          </div>
          
          {/* Generated Images */}
          <div className="order-1 lg:order-2">
            <GeneratedImages images={images} />
          </div>
        </div>
      </div>
    </div>
  )
}
