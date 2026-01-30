'use client'

import { useState, useRef, useEffect } from 'react'
import { SparklesIcon, PhotoIcon, XMarkIcon, BookmarkSquareIcon } from '@heroicons/react/24/outline'
import { generateGrouping, updatePrompt } from '@/services/api'
import { useProvider } from '@/contexts/ProviderContext'
import { useToast } from '@/contexts/ToastContext'

interface ImageGroupingFormProps {
  onImageGenerated: (image: any) => void
  isGenerating: boolean
  setIsGenerating: (value: boolean) => void
  initialPrompt?: string
  initialPromptId?: number
}

export default function ImageGroupingForm({ 
  onImageGenerated, 
  isGenerating, 
  setIsGenerating,
  initialPrompt = '',
  initialPromptId
}: ImageGroupingFormProps) {
  const { provider } = useProvider()
  const { addToast } = useToast()
  const [prompt, setPrompt] = useState(initialPrompt)
  const [isSaving, setIsSaving] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [previewUrls, setPreviewUrls] = useState<string[]>([])
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [retryAttempt, setRetryAttempt] = useState(0)
  const [isCancelled, setIsCancelled] = useState(false)
  const cancelRef = useRef(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Update prompt when initialPrompt prop changes
  useEffect(() => {
    if (initialPrompt) {
      setPrompt(initialPrompt)
    }
  }, [initialPrompt])

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return

    const newFiles: File[] = []
    const newPreviewUrls: string[] = []

    Array.from(files).forEach((file) => {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        setError(`Invalid file type: ${file.name}. Please select JPEG, PNG, or WebP files`)
        return
      }

      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError(`File too large: ${file.name}. Maximum size is 10MB`)
        return
      }

      newFiles.push(file)
      const url = URL.createObjectURL(file)
      newPreviewUrls.push(url)
    })

    if (newFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...newFiles])
      setPreviewUrls(prev => [...prev, ...newPreviewUrls])
      setError('')
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files)
    // Reset input to allow selecting the same files again
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    handleFileSelect(e.dataTransfer.files)
  }

  const removeImage = (index: number) => {
    // Revoke the preview URL
    if (previewUrls[index]) {
      URL.revokeObjectURL(previewUrls[index])
    }
    
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
    setPreviewUrls(prev => prev.filter((_, i) => i !== index))
    setError('')
  }

  const clearAllImages = () => {
    previewUrls.forEach(url => URL.revokeObjectURL(url))
    setSelectedFiles([])
    setPreviewUrls([])
    setError('')
  }

  const handleCancel = () => {
    cancelRef.current = true
    setIsCancelled(true)
    setIsGenerating(false)
    setError('Generation cancelled')
    setTimeout(() => {
      setRetryAttempt(0)
    }, 1000)
  }

  const handleSavePrompt = async () => {
    if (initialPromptId == null || !prompt.trim() || prompt.length > 2000) return
    if (prompt.trim() === initialPrompt.trim()) return
    setIsSaving(true)
    try {
      await updatePrompt(initialPromptId, prompt.trim())
      addToast({
        type: 'success',
        title: 'Prompt saved',
        message: 'Prompt text has been updated successfully.'
      })
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Failed to save prompt'
      addToast({
        type: 'error',
        title: 'Save failed',
        message: typeof message === 'string' ? message : 'Failed to save prompt.'
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    setError('')
    
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    if (prompt.length > 2000) {
      setError('Prompt too long (max 2000 characters)')
      return
    }

    if (selectedFiles.length === 0) {
      setError('Please select at least one person image')
      return
    }

    if (selectedFiles.length > 10) {
      setError('Maximum 10 images allowed')
      return
    }

    setError('')
    setRetryAttempt(0)
    setIsCancelled(false)
    cancelRef.current = false
    setIsGenerating(true)

    try {
      const response = await generateGrouping(
        prompt, 
        selectedFiles, 
        provider, 
        (attempt) => {
          setRetryAttempt(attempt)
        },
        () => cancelRef.current,
        initialPromptId
      )
      
      onImageGenerated({
        id: response.id,
        prompt,
        imageUrl: response.generated_image_url || '/placeholder-image.jpg',
        referenceImageUrl: response.reference_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: 'grouping'
      })
    } catch (err: any) {
      console.error('Image grouping error:', err)
      
      if (cancelRef.current || err?.message === 'Image generation cancelled by user') {
        setError('Image generation cancelled')
        setIsCancelled(true)
      } else {
        const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to generate image. Retrying...'
        setError(errorMessage)
      }
    } finally {
      setIsGenerating(false)
      if (!cancelRef.current) {
        setRetryAttempt(0)
      }
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-100 mb-6">
        Generate Group Image
      </h3>
      
      <form 
        onSubmit={handleSubmit} 
        className="space-y-4" 
        noValidate
      >
        {/* Multiple Person Images Upload */}
        <div>
          {selectedFiles.length === 0 ? (
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer ${
                dragActive 
                  ? 'border-teal-500 bg-[#1a2332]/80' 
                  : 'border-[#2a3441] hover:border-teal-500/50 hover:bg-[#1a2332]/40'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-500 mb-3" />
              <p className="text-sm text-gray-300 mb-1">
                Click to upload person images
              </p>
              <p className="text-xs text-gray-500">
                PNG, JPG, WebP up to 10MB each (max 10 images)
              </p>
              {dragActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 animate-pulse"></div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileInputChange}
                className="hidden"
              />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-300">
                  {selectedFiles.length} image{selectedFiles.length !== 1 ? 's' : ''} selected
                </p>
                <button
                  type="button"
                  onClick={clearAllImages}
                  className="text-xs text-red-400 hover:text-red-300 transition-colors"
                >
                  Clear All
                </button>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {selectedFiles.map((file, index) => (
                  <div key={index} className="relative group">
                    <div className="rounded-lg overflow-hidden border border-[#2a3441]">
                      <img
                        src={previewUrls[index]}
                        alt={`Preview ${index + 1}`}
                        className="w-full h-32 object-cover"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="absolute top-1 right-1 bg-red-500/90 hover:bg-red-600 text-white rounded-full p-1 transition-colors shadow-lg opacity-0 group-hover:opacity-100"
                    >
                      <XMarkIcon className="h-3 w-3" />
                    </button>
                    <p className="text-xs text-gray-500 mt-1 truncate" title={file.name}>
                      {file.name}
                    </p>
                  </div>
                ))}
              </div>
              {selectedFiles.length < 10 && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full border-2 border-dashed border-[#2a3441] rounded-lg p-4 text-center text-sm text-gray-400 hover:border-teal-500/50 hover:text-gray-300 transition-colors"
                >
                  + Add More Images
                </button>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileInputChange}
                className="hidden"
              />
            </div>
          )}
        </div>

        {/* Prompt Input */}
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
            Describe how you want to use these person images
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Create a group photo with all these people in a park setting..."
            className="input-field min-h-[120px] resize-none"
            disabled={isGenerating}
            rows={4}
          />
          <div className="flex justify-between items-center mt-1 flex-wrap gap-2">
            <span className={`text-xs ${prompt.length > 2000 ? 'text-red-400' : 'text-gray-500'}`}>
              {prompt.length}/2000 characters
            </span>
            {prompt.length > 2000 && (
              <span className="text-xs text-red-400">
                Prompt too long!
              </span>
            )}
            {initialPromptId != null && (
              <button
                type="button"
                onClick={handleSavePrompt}
                disabled={
                  isSaving ||
                  isGenerating ||
                  !prompt.trim() ||
                  prompt.trim() === initialPrompt.trim() ||
                  prompt.length > 2000
                }
                className="btn-secondary text-sm inline-flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? (
                  <>
                    <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-gray-400 border-t-transparent" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <BookmarkSquareIcon className="h-4 w-4" />
                    <span>Save prompt</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="text-red-300 text-sm bg-red-900/20 border border-red-500/30 rounded-lg p-3">
            {error}
          </div>
        )}

        {/* Retry Progress */}
        {isGenerating && retryAttempt > 0 && (
          <div className="text-teal-300 text-sm bg-teal-900/20 border border-teal-500/30 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-teal-400 border-t-transparent"></div>
                <span>Retrying... Attempt {retryAttempt} of 20</span>
              </div>
              <button
                type="button"
                onClick={handleCancel}
                className="px-3 py-1 text-xs bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 rounded transition-colors"
              >
                Stop
              </button>
            </div>
          </div>
        )}

        <div className="flex space-x-2">
          <button
            type="submit"
            disabled={isGenerating || !prompt.trim() || selectedFiles.length === 0 || prompt.length > 2000}
            className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>
                  {retryAttempt > 0 ? `Retrying... (Attempt ${retryAttempt}/20)` : 'Generating...'}
                </span>
              </>
            ) : (
              <>
                <SparklesIcon className="h-4 w-4" />
                <span>Generate Group Image</span>
              </>
            )}
          </button>
          {isGenerating && (
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 btn-secondary flex items-center justify-center space-x-2"
            >
              <XMarkIcon className="h-4 w-4" />
              <span>Cancel</span>
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

