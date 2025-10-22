'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import ImageGenerationForm from '@/components/ImageGenerationForm'
import GeneratedImages from '@/components/GeneratedImages'

function GeneratePageContent() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [initialPrompt, setInitialPrompt] = useState('')
  const searchParams = useSearchParams()

  // Read prompt from URL parameters
  useEffect(() => {
    const prompt = searchParams.get('prompt')
    if (prompt) {
      setInitialPrompt(decodeURIComponent(prompt))
    }
  }, [searchParams])

  const handleImageGenerated = (newImage: any) => {
    setImages(prev => [newImage, ...prev])
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image Generation Form */}
          <div className="order-2 lg:order-1">
            <ImageGenerationForm 
              onImageGenerated={handleImageGenerated}
              isGenerating={isGenerating}
              setIsGenerating={setIsGenerating}
              initialPrompt={initialPrompt}
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

export default function GeneratePage() {
  return (
    <Suspense fallback={<div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div></div>}>
      <GeneratePageContent />
    </Suspense>
  )
}
