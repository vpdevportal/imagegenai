'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { SparklesIcon, ArrowPathIcon, XMarkIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'
import { generatePromptFromImage } from '@/services/api'
import { useToast } from '@/contexts/ToastContext'
import { QueueItem } from '@/types'

interface ImageToPromptFormProps {
  onPromptGenerated: (prompt: string, thumbnail: string) => void
}

export default function ImageToPromptForm({ onPromptGenerated }: ImageToPromptFormProps) {
  const [queue, setQueue] = useState<QueueItem[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { addToast } = useToast()
  const processingRef = useRef(false)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    const newItems: QueueItem[] = []
    const promises: Promise<void>[] = []

    Array.from(files).forEach((file) => {
      const id = `${Date.now()}-${Math.random()}`
      const promise = new Promise<void>((resolve) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          newItems.push({
            id,
            file,
            preview: e.target?.result as string,
            style: 'photorealistic',
            status: 'pending'
          })
          resolve()
        }
        reader.readAsDataURL(file)
      })
      promises.push(promise)
    })

    Promise.all(promises).then(() => {
      setQueue(prev => [...prev, ...newItems])
      addToast({
        type: 'success',
        title: 'Images Added',
        message: `${newItems.length} image(s) added to queue`
      })
    })

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Process queue sequentially
  const processQueue = useCallback(async () => {
    if (processingRef.current || queue.length === 0) return
    
    const pendingItem = queue.find(item => item.status === 'pending')
    if (!pendingItem) {
      // Check if all completed
      const allCompleted = queue.every(item => item.status === 'completed')
      if (allCompleted && queue.length > 0 && processingRef.current) {
        addToast({
          type: 'success',
          title: 'All Prompts Generated',
          message: `Successfully generated ${queue.length} prompt(s)`
        })
      }
      return
    }

    processingRef.current = true
    setIsProcessing(true)

    // Update status to processing
    setQueue(prev => prev.map(item => 
      item.id === pendingItem.id ? { ...item, status: 'processing' as const } : item
    ))

    try {
      const result = await generatePromptFromImage(
        pendingItem.file
      )
      
      if (result.success) {
        // Update queue item with result
        setQueue(prev => prev.map(item => 
          item.id === pendingItem.id 
            ? { 
                ...item, 
                status: 'completed' as const,
                prompt: result.prompt,
                thumbnail: result.thumbnail
              } 
            : item
        ))
        
        // Notify parent component
        onPromptGenerated(result.prompt, result.thumbnail)
      }
    } catch (error: any) {
      console.error('Error generating prompt:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to generate prompt'
      
      // Update queue item with error
      setQueue(prev => prev.map(item => 
        item.id === pendingItem.id 
          ? { 
              ...item, 
              status: 'error' as const,
              error: errorMessage
            } 
          : item
      ))
      
      addToast({
        type: 'error',
        title: 'Generation Failed',
        message: errorMessage
      })
    } finally {
      // Reset processing flag and state
      processingRef.current = false
      setIsProcessing(false)
    }
  }, [queue, addToast, onPromptGenerated])

  // Auto-process queue when items are added or status changes
  useEffect(() => {
    if (queue.some(item => item.status === 'pending') && !processingRef.current) {
      processQueue()
    }
  }, [queue, processQueue])

  const removeFromQueue = (id: string) => {
    setQueue(prev => prev.filter(item => item.id !== id))
  }

  const clearQueue = () => {
    setQueue([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const retryItem = (id: string) => {
    setQueue(prev => prev.map(item => 
      item.id === id ? { ...item, status: 'pending' as const, error: undefined } : item
    ))
  }

  const pendingCount = queue.filter(item => item.status === 'pending').length
  const processingCount = queue.filter(item => item.status === 'processing').length
  const completedCount = queue.filter(item => item.status === 'completed').length
  const errorCount = queue.filter(item => item.status === 'error').length

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-2 rounded-lg shadow-lg">
            <SparklesIcon className="h-5 w-5 text-white" />
          </div>
          <h2 className="text-2xl font-bold gradient-text">Upload Images</h2>
        </div>
        {queue.length > 0 && (
          <button
            onClick={clearQueue}
            disabled={isProcessing}
            className="text-sm text-red-400 hover:text-red-300 font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Clear All
          </button>
        )}
      </div>

      {/* File Upload Area */}
      <div className="mb-6">
        <div
          onClick={() => !isProcessing && fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
            isProcessing 
              ? 'opacity-50 cursor-not-allowed border-gray-700' 
              : 'border-gray-700 hover:border-purple-500 hover:bg-purple-900/20 cursor-pointer'
          }`}
        >
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 rounded-2xl w-20 h-20 mx-auto mb-4 flex items-center justify-center shadow-lg">
            <svg className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
            </svg>
          </div>
          <p className="text-sm font-semibold text-gray-300 mb-2">
            Click to upload images (multiple selection supported)
          </p>
          <p className="text-xs text-gray-400">
            PNG, JPG, GIF up to 10MB each
          </p>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileSelect}
          disabled={isProcessing}
          className="hidden"
        />
      </div>

      {/* Queue Status */}
      {queue.length > 0 && (
        <div className="mb-6 p-4 bg-gray-800/50 rounded-xl border border-gray-700/50">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-300">Queue Status</h3>
            {isProcessing && (
              <div className="flex items-center text-purple-400">
                <ArrowPathIcon className="h-4 w-4 animate-spin mr-2" />
                <span className="text-xs font-medium">Processing...</span>
              </div>
            )}
          </div>
          <div className="grid grid-cols-4 gap-2 text-center text-xs">
            <div className="bg-gray-700/50 rounded-lg px-2 py-2 border border-gray-600/50">
              <div className="font-semibold text-gray-200">{pendingCount}</div>
              <div className="text-gray-400">Pending</div>
            </div>
            <div className="bg-blue-900/50 rounded-lg px-2 py-2 border border-blue-700/50">
              <div className="font-semibold text-blue-300">{processingCount}</div>
              <div className="text-blue-400">Processing</div>
            </div>
            <div className="bg-green-900/50 rounded-lg px-2 py-2 border border-green-700/50">
              <div className="font-semibold text-green-300">{completedCount}</div>
              <div className="text-green-400">Completed</div>
            </div>
            <div className="bg-red-900/50 rounded-lg px-2 py-2 border border-red-700/50">
              <div className="font-semibold text-red-300">{errorCount}</div>
              <div className="text-red-400">Failed</div>
            </div>
          </div>
        </div>
      )}

      {/* Queue Items */}
      {queue.length > 0 && (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {queue.map((item) => (
            <div
              key={item.id}
              className={`border-2 rounded-xl p-3 flex items-center space-x-3 transition-all duration-300 ${
                item.status === 'processing' ? 'border-purple-500/50 bg-purple-900/20' :
                item.status === 'completed' ? 'border-green-500/50 bg-green-900/20' :
                item.status === 'error' ? 'border-red-500/50 bg-red-900/20' :
                'border-gray-700 bg-gray-800/50'
              }`}
            >
              {/* Thumbnail */}
              <div className="w-16 h-16 flex-shrink-0 relative bg-gray-900 rounded-lg overflow-hidden border border-gray-700">
                <img
                  src={item.preview}
                  alt="Preview"
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs font-medium text-gray-300 truncate">
                    {item.file.name}
                  </p>
                  <div className="flex items-center space-x-1 ml-2">
                    {item.status === 'pending' && (
                      <span className="text-xs text-gray-400 px-2 py-0.5 bg-gray-700/50 rounded-lg border border-gray-600">
                        Pending
                      </span>
                    )}
                    {item.status === 'processing' && (
                      <span className="text-xs text-purple-300 px-2 py-0.5 bg-purple-900/50 rounded-lg border border-purple-700/50 flex items-center">
                        <ArrowPathIcon className="h-3 w-3 animate-spin mr-1" />
                        Processing
                      </span>
                    )}
                    {item.status === 'completed' && (
                      <span className="text-xs text-green-300 px-2 py-0.5 bg-green-900/50 rounded-lg border border-green-700/50 flex items-center">
                        <CheckCircleIcon className="h-3 w-3 mr-1" />
                        Done
                      </span>
                    )}
                    {item.status === 'error' && (
                      <span className="text-xs text-red-300 px-2 py-0.5 bg-red-900/50 rounded-lg border border-red-700/50 flex items-center">
                        <ExclamationCircleIcon className="h-3 w-3 mr-1" />
                        Failed
                      </span>
                    )}
                  </div>
                </div>
                {item.error && (
                  <div className="text-xs text-red-400 mt-1 truncate">
                    {item.error}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-1">
                {item.status === 'error' && (
                  <button
                    onClick={() => retryItem(item.id)}
                    className="p-1.5 text-blue-400 hover:text-blue-300 rounded-lg hover:bg-blue-900/30 transition-colors"
                    title="Retry"
                  >
                    <ArrowPathIcon className="h-4 w-4" />
                  </button>
                )}
                <button
                  onClick={() => removeFromQueue(item.id)}
                  disabled={item.status === 'processing'}
                  className="p-1.5 text-red-400 hover:text-red-300 rounded-lg hover:bg-red-900/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title="Remove"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {queue.length === 0 && (
        <div className="text-center py-8 text-gray-400 text-sm font-medium">
          No images in queue. Upload images to get started!
        </div>
      )}
    </div>
  )
}
