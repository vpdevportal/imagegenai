'use client'

import { useState, useRef, useEffect } from 'react'
import { SparklesIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import { generatePromptFromImage, getInspireStyles } from '@/lib/api'
import { useToast } from '@/contexts/ToastContext'

interface ImageToPromptFormProps {
  onPromptGenerated: (prompt: string, thumbnail: string) => void
}

export default function ImageToPromptForm({ onPromptGenerated }: ImageToPromptFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [style, setStyle] = useState('photorealistic')
  const [detailLevel, setDetailLevel] = useState('detailed')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedPrompt, setGeneratedPrompt] = useState<string | null>(null)
  const [isSavedToDatabase, setIsSavedToDatabase] = useState(false)
  const [styles, setStyles] = useState<Array<{ value: string; label: string }>>([])
  const [detailLevels, setDetailLevels] = useState<Array<{ value: string; label: string }>>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { addToast } = useToast()

  // Load styles on component mount
  useEffect(() => {
    const loadStyles = async () => {
      try {
        const data = await getInspireStyles()
        setStyles(data.styles)
        setDetailLevels(data.detail_levels)
      } catch (error) {
        console.error('Error loading styles:', error)
        addToast({
          type: 'warning',
          title: 'Failed to Load Styles',
          message: 'Using default styles. Some options may not be available.'
        })
      }
    }
    loadStyles()
  }, [addToast])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setGeneratedPrompt(null)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleGeneratePrompt = async () => {
    if (!selectedFile) return

    setIsGenerating(true)
    try {
      const result = await generatePromptFromImage(selectedFile, style, detailLevel)
      
      if (result.success) {
        setGeneratedPrompt(result.prompt)
        setIsSavedToDatabase(result.saved_to_database)
        onPromptGenerated(result.prompt, result.thumbnail)
        
        // Show success toast
        addToast({
          type: 'success',
          title: 'Prompt Generated Successfully!',
          message: result.saved_to_database 
            ? 'Prompt has been generated and saved to your collection.' 
            : 'Prompt has been generated successfully.'
        })
      }
    } catch (error: any) {
      console.error('Error generating prompt:', error)
      
      // Show error toast with more specific error message
      const errorMessage = error?.response?.data?.detail || error?.message || 'An unexpected error occurred'
      addToast({
        type: 'error',
        title: 'Failed to Generate Prompt',
        message: errorMessage
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleClear = () => {
    setSelectedFile(null)
    setPreview(null)
    setGeneratedPrompt(null)
    setIsSavedToDatabase(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Upload Image</h2>

      {/* File Upload Area */}
      <div className="mb-6">
        {!preview ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-400 cursor-pointer transition-colors"
          >
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
            </svg>
            <p className="text-sm text-gray-600 mb-2">
              Click to upload an image
            </p>
            <p className="text-xs text-gray-500">
              PNG, JPG, GIF up to 10MB
            </p>
          </div>
          ) : (
            <div className="relative group">
              <div className="aspect-square relative bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-full object-contain"
                />
              </div>
              <button
                onClick={handleClear}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1.5 hover:bg-red-600 transition-colors shadow-sm opacity-0 group-hover:opacity-100"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Style and Detail Level Selection */}
      {selectedFile && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Style
            </label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {styles.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Detail Level
            </label>
            <select
              value={detailLevel}
              onChange={(e) => setDetailLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {detailLevels.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Generate Button */}
      {selectedFile && (
        <button
          onClick={handleGeneratePrompt}
          disabled={isGenerating}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {isGenerating ? (
            <>
              <ArrowPathIcon className="h-5 w-5 animate-spin" />
              <span>Generating Prompt...</span>
            </>
          ) : (
            <>
              <SparklesIcon className="h-5 w-5" />
              <span>Generate Prompt</span>
            </>
          )}
        </button>
      )}

      {/* Generated Prompt Display */}
      {generatedPrompt && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-700">Generated Prompt:</h3>
            {isSavedToDatabase && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Saved
              </span>
            )}
          </div>
          <p className="text-sm text-gray-900 bg-white p-3 rounded border">
            {generatedPrompt}
          </p>
          <button
            onClick={() => navigator.clipboard.writeText(generatedPrompt)}
            className="mt-2 text-xs text-purple-600 hover:text-purple-700 font-medium"
          >
            Copy to clipboard
          </button>
        </div>
      )}
    </div>
  )
}
