'use client'

import { useState } from 'react'
import ImageToPromptForm from '@/components/ImageToPromptForm'
import GeneratedImages from '@/components/GeneratedImages'

export default function InspirePage() {
  const [images, setImages] = useState<any[]>([])
  const [generatedPrompts, setGeneratedPrompts] = useState<Array<{
    prompt: string
    thumbnail: string
    timestamp: Date
  }>>([])

  const handlePromptGenerated = (prompt: string, thumbnail: string) => {
    const newPrompt = {
      prompt,
      thumbnail,
      timestamp: new Date()
    }
    setGeneratedPrompts(prev => [newPrompt, ...prev])
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image to Prompt Form */}
          <div className="order-2 lg:order-1">
            <ImageToPromptForm onPromptGenerated={handlePromptGenerated} />
          </div>
          
          {/* Generated Prompts */}
          <div className="order-1 lg:order-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Prompts</h3>
              
              {generatedPrompts.length === 0 ? (
                <div className="text-center py-8">
                  <div className="bg-gray-100 rounded-full p-3 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                    <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <p className="text-gray-500 text-sm">Upload an image to generate prompts</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {generatedPrompts.map((item, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                      <div className="flex items-start space-x-3">
                        <img
                          src={item.thumbnail}
                          alt="Generated thumbnail"
                          className="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900 mb-2">{item.prompt}</p>
                          <p className="text-xs text-gray-500">
                            {item.timestamp.toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
