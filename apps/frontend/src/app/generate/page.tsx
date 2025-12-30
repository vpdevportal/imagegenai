'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import ImageGenerationForm from '@/components/ImageGenerationForm'
import GeneratedImages from '@/components/GeneratedImages'

function GeneratePageContent() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [initialPrompt, setInitialPrompt] = useState('')
  const [promptId, setPromptId] = useState<number | undefined>(undefined)
  const searchParams = useSearchParams()

  // Read prompt ID and prompt text from URL parameters
  useEffect(() => {
    const promptIdParam = searchParams.get('promptId')
    const promptParam = searchParams.get('prompt')
    
    if (promptIdParam) {
      const id = parseInt(promptIdParam, 10)
      if (!isNaN(id)) {
        setPromptId(id)
        // Fetch prompt text from API to populate the form
        import('@/services/api').then(({ getPrompt }) => {
          getPrompt(id)
            .then((prompt) => {
              setInitialPrompt(prompt.prompt_text)
            })
            .catch((err) => {
              console.error('Failed to fetch prompt:', err)
            })
        })
      }
    } else if (promptParam) {
      // Fallback to old prompt parameter for backward compatibility
      setInitialPrompt(decodeURIComponent(promptParam))
      setPromptId(undefined)
    }
  }, [searchParams])

  const handleImageGenerated = (newImage: any) => {
    setImages(prev => [newImage, ...prev])
  }

  const handleDeleteImage = (imageId: string | number) => {
    setImages(prev => prev.filter(img => img.id !== imageId))
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Image Generation Form */}
          <div className="order-1 lg:order-1">
            <ImageGenerationForm 
              onImageGenerated={handleImageGenerated}
              isGenerating={isGenerating}
              setIsGenerating={setIsGenerating}
              initialPrompt={initialPrompt}
              initialPromptId={promptId}
            />
          </div>
          
          {/* Generated Images */}
          <div className="order-2 lg:order-2">
            <GeneratedImages images={images} onDelete={handleDeleteImage} />
          </div>
        </div>
      </div>
    </div>
  )
}

export const dynamic = 'force-dynamic'

export default function GeneratePage() {
  return (
    <Suspense fallback={<div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div></div>}>
      <GeneratePageContent />
    </Suspense>
  )
}
