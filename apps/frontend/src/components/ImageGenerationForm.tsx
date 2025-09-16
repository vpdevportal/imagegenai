'use client'

import { useState } from 'react'
import { SparklesIcon } from '@heroicons/react/24/outline'
import { generateImage } from '@/lib/api'

interface ImageGenerationFormProps {
  onImageGenerated: (image: any) => void
  isGenerating: boolean
  setIsGenerating: (value: boolean) => void
}

export default function ImageGenerationForm({ 
  onImageGenerated, 
  isGenerating, 
  setIsGenerating 
}: ImageGenerationFormProps) {
  const [prompt, setPrompt] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setError('')
    setIsGenerating(true)

    try {
      const response = await generateImage(prompt)
      onImageGenerated({
        id: Date.now(),
        prompt,
        imageUrl: response.generated_image_url || '/placeholder-image.jpg',
        status: response.status,
        createdAt: new Date().toISOString()
      })
      setPrompt('')
    } catch (err) {
      setError('Failed to generate image. Please try again.')
      console.error('Image generation error:', err)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Generate New Image
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
            Describe the image you want to generate
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="A serene mountain landscape at sunset with a lake reflecting the sky..."
            className="input-field min-h-[120px] resize-none"
            disabled={isGenerating}
            rows={4}
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isGenerating || !prompt.trim()}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating...</span>
            </>
          ) : (
            <>
              <SparklesIcon className="h-4 w-4" />
              <span>Generate Image</span>
            </>
          )}
        </button>
      </form>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-2">Tips for better results:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Be descriptive and specific</li>
          <li>• Include style preferences (photorealistic, artistic, etc.)</li>
          <li>• Mention lighting and mood</li>
          <li>• Add details about composition</li>
        </ul>
      </div>
    </div>
  )
}
