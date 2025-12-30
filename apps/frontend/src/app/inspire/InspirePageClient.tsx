'use client'

import { useState } from 'react'
import Image from 'next/image'
import ImageToPromptForm from '@/components/ImageToPromptForm'
import GeneratedImages from '@/components/GeneratedImages'

export default function InspirePageClient() {
  const [images, setImages] = useState<any[]>([])
  const [generatedPrompts, setGeneratedPrompts] = useState<Array<{
    prompt: string
    thumbnail: string
    timestamp: Date
  }>>([])

  const handlePromptGenerated = (prompt: string, thumbnail: string) => {
    console.log('Received prompt and thumbnail:', { prompt: prompt.substring(0, 50) + '...', thumbnail: thumbnail ? thumbnail.substring(0, 50) + '...' : 'null' })
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Image to Prompt Form */}
          <div className="order-1 lg:order-1">
            <ImageToPromptForm onPromptGenerated={handlePromptGenerated} />
          </div>
          
          {/* Generated Prompts */}
          <div className="order-2 lg:order-2">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Generated Prompts</h3>
              
              {generatedPrompts.length === 0 ? (
                <div className="text-center py-8">
                  <div className="bg-[#1a2332]/50 rounded-full p-3 w-12 h-12 mx-auto mb-4 flex items-center justify-center border border-[#2a3441]">
                    <svg className="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <p className="text-gray-500 text-sm">Upload an image to generate prompts</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {generatedPrompts.map((item, index) => (
                    <div key={index} className="border border-[#2a3441] rounded-lg p-4 hover:border-teal-500/30 transition-all duration-200 bg-[#1a2332]/30">
                      <div className="flex items-start space-x-3">
                        <div className="w-16 h-16 flex-shrink-0 relative bg-[#0a1929] rounded-lg overflow-hidden border border-[#2a3441]">
                          {item.thumbnail ? (
                            <Image
                              src={item.thumbnail}
                              alt="Generated thumbnail"
                              fill
                              className="object-cover"
                              onError={(e) => {
                                console.error('Failed to load thumbnail:', e)
                                e.currentTarget.style.display = 'none'
                              }}
                            />
                          ) : (
                            <div className="flex items-center justify-center h-full text-gray-600">
                              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-200 mb-2">{item.prompt}</p>
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

