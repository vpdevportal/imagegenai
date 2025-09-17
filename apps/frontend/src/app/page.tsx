'use client'

import { useState } from 'react'
import { PhotoIcon, SparklesIcon } from '@heroicons/react/24/outline'
import ImageGenerationForm from '@/components/ImageGenerationForm'
import GeneratedImages from '@/components/GeneratedImages'

export default function Home() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleImageGenerated = (newImage: any) => {
    setImages(prev => [newImage, ...prev])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-2">
            <div className="flex items-center space-x-2">
              <div className="bg-primary-600 p-1.5 rounded-md">
                <SparklesIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ImageGenAI</h1>
                <p className="text-xs text-gray-500">AI-Powered Image Generation</p>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              Powered by Advanced AI
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - This will grow to fill available space */}
      <main className="flex-1 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
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
      </main>

      {/* Footer - This will stick to the bottom */}
      <footer className="bg-gray-900 text-white py-8 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2024 ImageGenAI. Built with FastAPI and Next.js
          </p>
        </div>
      </footer>
    </div>
  )
}
