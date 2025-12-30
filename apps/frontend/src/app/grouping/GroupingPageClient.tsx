'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import ImageGroupingForm from '@/components/ImageGroupingForm'
import GeneratedImages from '@/components/GeneratedImages'
import { getPrompt } from '@/services/api'

export default function GroupingPageClient() {
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
        getPrompt(id)
          .then((prompt) => {
            setInitialPrompt(prompt.prompt_text)
          })
          .catch((err) => {
            console.error('Failed to fetch prompt:', err)
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
          {/* Image Grouping Form */}
          <div className="order-1 lg:order-1">
            <ImageGroupingForm 
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

