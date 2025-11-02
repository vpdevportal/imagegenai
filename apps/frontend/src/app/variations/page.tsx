'use client'

import { useState } from 'react'
import ImageVariationForm from '@/components/ImageVariationForm'
import GeneratedImages from '@/components/GeneratedImages'

export default function VariationsPage() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleVariationGenerated = (newVariation: any) => {
    setImages(prev => [newVariation, ...prev])
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image Variation Form */}
          <div className="order-2 lg:order-1">
            <ImageVariationForm 
              onVariationGenerated={handleVariationGenerated}
              isGenerating={isGenerating}
              setIsGenerating={setIsGenerating}
            />
          </div>
          
          {/* Generated Variations */}
          <div className="order-1 lg:order-2">
            <GeneratedImages images={images} />
          </div>
        </div>
      </div>
    </div>
  )
}

