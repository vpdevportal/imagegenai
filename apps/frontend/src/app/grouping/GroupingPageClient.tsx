'use client'

import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import ImageGroupingForm from '@/components/ImageGroupingForm'
import GeneratedImages from '@/components/GeneratedImages'
import { getPrompt, getPromptThumbnail } from '@/services/api'

export default function GroupingPageClient() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [initialPrompt, setInitialPrompt] = useState('')
  const [promptId, setPromptId] = useState<number | undefined>(undefined)
  const [promptThumbnailUrl, setPromptThumbnailUrl] = useState<string | null>(null)
  const thumbnailUrlRef = useRef<string | null>(null)
  const searchParams = useSearchParams()

  useEffect(() => {
    const prev = thumbnailUrlRef.current
    if (prev && prev !== promptThumbnailUrl) {
      URL.revokeObjectURL(prev)
    }
    thumbnailUrlRef.current = promptThumbnailUrl
    return () => {
      if (thumbnailUrlRef.current) {
        URL.revokeObjectURL(thumbnailUrlRef.current)
        thumbnailUrlRef.current = null
      }
    }
  }, [promptThumbnailUrl])

  // Read prompt ID and prompt text from URL parameters; fetch thumbnail if prompt has one
  useEffect(() => {
    const promptIdParam = searchParams.get('promptId')
    const promptParam = searchParams.get('prompt')

    if (promptIdParam) {
      const id = parseInt(promptIdParam, 10)
      if (!isNaN(id)) {
        setPromptId(id)
        setPromptThumbnailUrl(null)
        getPrompt(id)
          .then((prompt) => {
            setInitialPrompt(prompt.prompt_text)
            if (prompt.thumbnail_mime) {
              return getPromptThumbnail(id).then((url) => {
                setPromptThumbnailUrl(url)
              })
            }
          })
          .catch((err) => {
            console.error('Failed to fetch prompt:', err)
          })
      }
    } else if (promptParam) {
      setInitialPrompt(decodeURIComponent(promptParam))
      setPromptId(undefined)
      setPromptThumbnailUrl(null)
    }
  }, [searchParams])

  const handleImageGenerated = (newImage: any) => {
    setImages(prev => [newImage, ...prev])
  }

  const handleDeleteImage = (imageId: string | number) => {
    setImages(prev => prev.filter(img => img.id !== imageId))
  }

  const handleClearAll = () => {
    setImages([])
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
              promptThumbnailUrl={promptThumbnailUrl}
            />
          </div>
          
          {/* Generated Images */}
          <div className="order-2 lg:order-2">
            <GeneratedImages images={images} onDelete={handleDeleteImage} onClearAll={handleClearAll} />
          </div>
        </div>
      </div>
    </div>
  )
}

