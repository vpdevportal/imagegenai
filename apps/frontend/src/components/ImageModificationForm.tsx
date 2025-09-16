'use client'

import { useState, useRef } from 'react'
import { PhotoIcon, ArrowUpTrayIcon, ClipboardDocumentIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { modifyImage, modifyPastedImage } from '@/lib/api'

interface ImageModificationFormProps {
  onImageModified: (image: any) => void
  isModifying: boolean
  setIsModifying: (value: boolean) => void
}

export default function ImageModificationForm({ 
  onImageModified, 
  isModifying, 
  setIsModifying 
}: ImageModificationFormProps) {
  const [prompt, setPrompt] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [pasteMode, setPasteMode] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const pasteAreaRef = useRef<HTMLDivElement>(null)

  const handleFileSelect = (file: File) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      setError('Please select a valid image file (JPEG, PNG, or WebP)')
      return
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size is 10MB')
      return
    }

    setSelectedFile(file)
    setError('')
    
    // Create preview URL
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
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
    
    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile()
        if (file) {
          handleFileSelect(file)
          setPasteMode(false)
        }
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!prompt.trim()) {
      setError('Please enter a modification prompt')
      return
    }

    if (!selectedFile && !pasteMode) {
      setError('Please select an image or paste one')
      return
    }

    setError('')
    setIsModifying(true)

    try {
      let response
      
      if (pasteMode && previewUrl) {
        // Handle pasted image (base64)
        response = await modifyPastedImage({
          prompt,
          image: previewUrl,
          metadata: {
            source: 'paste',
            timestamp: new Date().toISOString()
          }
        })
      } else if (selectedFile) {
        // Handle uploaded file
        const formData = new FormData()
        formData.append('image', selectedFile)
        formData.append('prompt', prompt)
        formData.append('metadata', JSON.stringify({
          source: 'upload',
          filename: selectedFile.name,
          size: selectedFile.size,
          type: selectedFile.type,
          timestamp: new Date().toISOString()
        }))

        response = await modifyImage(formData)
      } else {
        throw new Error('No image provided')
      }

      onImageModified({
        id: response.id,
        prompt,
        originalImageUrl: response.original_image_url,
        modifiedImageUrl: response.modified_image_url,
        status: response.status,
        createdAt: response.created_at,
        type: 'modification'
      })
      
      // Reset form
      setPrompt('')
      setSelectedFile(null)
      setPreviewUrl(null)
      setPasteMode(false)
      
    } catch (err) {
      setError('Failed to modify image. Please try again.')
      console.error('Image modification error:', err)
    } finally {
      setIsModifying(false)
    }
  }

  const clearImage = () => {
    setSelectedFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
    setPasteMode(false)
    setError('')
  }

  const togglePasteMode = () => {
    setPasteMode(!pasteMode)
    if (!pasteMode) {
      clearImage()
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Modify Existing Image
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Image Input Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload or Paste Image
          </label>
          
          {!previewUrl ? (
            <div className="space-y-3">
              {/* Upload Area */}
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  dragActive 
                    ? 'border-primary-500 bg-primary-50' 
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <PhotoIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-600 mb-2">
                  Drag and drop an image here, or click to select
                </p>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="btn-primary text-sm"
                >
                  <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
                  Choose File
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileInputChange}
                  className="hidden"
                />
              </div>
              
              {/* Paste Option */}
              <div className="text-center">
                <span className="text-sm text-gray-500">or</span>
                <button
                  type="button"
                  onClick={togglePasteMode}
                  className="ml-2 btn-secondary text-sm"
                >
                  <ClipboardDocumentIcon className="h-4 w-4 mr-2" />
                  Paste Image
                </button>
              </div>
            </div>
          ) : (
            /* Preview Area */
            <div className="relative">
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="w-full h-full object-cover"
                />
              </div>
              <button
                type="button"
                onClick={clearImage}
                className="absolute top-2 right-2 p-1 bg-black bg-opacity-50 text-white rounded-full hover:bg-opacity-70"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          )}
          
          {/* Paste Mode Instructions */}
          {pasteMode && !previewUrl && (
            <div 
              ref={pasteAreaRef}
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50"
              onPaste={handlePaste}
              tabIndex={0}
            >
              <ClipboardDocumentIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-sm text-gray-600">
                Click here and paste your image (Ctrl+V or Cmd+V)
              </p>
            </div>
          )}
        </div>

        {/* Prompt Input */}
        <div>
          <label htmlFor="modify-prompt" className="block text-sm font-medium text-gray-700 mb-2">
            Describe how you want to modify the image
          </label>
          <textarea
            id="modify-prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Add a sunset background, change the color to blue, make it more artistic..."
            className="input-field min-h-[100px] resize-none"
            disabled={isModifying}
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
          disabled={isModifying || !prompt.trim() || (!selectedFile && !pasteMode)}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isModifying ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Modifying Image...</span>
            </>
          ) : (
            <>
              <PhotoIcon className="h-4 w-4" />
              <span>Modify Image</span>
            </>
          )}
        </button>
      </form>

      <div className="mt-6 p-4 bg-purple-50 rounded-lg">
        <h4 className="text-sm font-medium text-purple-900 mb-2">Tips for better modifications:</h4>
        <ul className="text-sm text-purple-800 space-y-1">
          <li>• Be specific about what you want to change</li>
          <li>• Mention style, colors, lighting, or composition changes</li>
          <li>• You can add elements, remove objects, or change backgrounds</li>
          <li>• Try prompts like "make it more vibrant" or "add a vintage effect"</li>
        </ul>
      </div>
    </div>
  )
}
