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
    <main className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <SparklesIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ImageGenAI</h1>
                <p className="text-sm text-gray-500">AI-Powered Image Generation</p>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Powered by Advanced AI
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Transform Your Ideas Into Stunning Images
          </h2>
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center">
              <PhotoIcon className="h-5 w-5 mr-1" />
              High Quality
            </div>
            <div className="flex items-center">
              <SparklesIcon className="h-5 w-5 mr-1" />
              AI Powered
            </div>
            <div className="flex items-center">
              <span className="h-2 w-2 bg-green-500 rounded-full mr-2"></span>
              Fast Generation
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="pb-16 px-4 sm:px-6 lg:px-8">
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
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2024 ImageGenAI. Built with FastAPI and Next.js
          </p>
        </div>
      </footer>
    </main>
  )
}
