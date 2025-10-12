'use client'

import { useState, useRef, useEffect } from 'react'
import { SparklesIcon, ArrowPathIcon, XMarkIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'
import { generatePromptFromImage, getInspireStyles } from '@/lib/api'
import { useToast } from '@/contexts/ToastContext'
import { QueueItem } from '@/types'

interface ImageToPromptFormProps {
  onPromptGenerated: (prompt: string, thumbnail: string) => void
}

export default function ImageToPromptForm({ onPromptGenerated }: ImageToPromptFormProps) {
  const [queue, setQueue] = useState<QueueItem[]>([])
  const [style, setStyle] = useState('photorealistic')
  const [detailLevel, setDetailLevel] = useState('detailed')
  const [isProcessing, setIsProcessing] = useState(false)
  const [styles, setStyles] = useState<Array<{ value: string; label: string }>>([])
  const [detailLevels, setDetailLevels] = useState<Array<{ value: string; label: string }>>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { addToast } = useToast()
  const processingRef = useRef(false)

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
            style,
            detailLevel,
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
  const processQueue = async () => {
    if (processingRef.current || queue.length === 0) return
    
    processingRef.current = true
    setIsProcessing(true)

    // Find the first pending item
    const pendingItem = queue.find(item => item.status === 'pending')
    if (!pendingItem) {
      processingRef.current = false
      setIsProcessing(false)
      
      // Check if all completed
      const allCompleted = queue.every(item => item.status === 'completed')
      if (allCompleted && queue.length > 0) {
        addToast({
          type: 'success',
          title: 'All Prompts Generated',
          message: `Successfully generated ${queue.length} prompt(s)`
        })
      }
      return
    }

    // Update status to processing
    setQueue(prev => prev.map(item => 
      item.id === pendingItem.id ? { ...item, status: 'processing' as const } : item
    ))

    try {
      const result = await generatePromptFromImage(
        pendingItem.file, 
        pendingItem.style, 
        pendingItem.detailLevel
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
    }

    // Continue processing next item
    processingRef.current = false
    setTimeout(() => processQueue(), 500)
  }

  // Auto-process queue when items are added
  useEffect(() => {
    if (queue.some(item => item.status === 'pending') && !processingRef.current) {
      processQueue()
    }
  }, [queue])

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
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Upload Images</h2>
        {queue.length > 0 && (
          <button
            onClick={clearQueue}
            disabled={isProcessing}
            className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Style and Detail Level Selection (Global) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Style
          </label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            disabled={isProcessing}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
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
            disabled={isProcessing}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
          >
            {detailLevels.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* File Upload Area */}
      <div className="mb-6">
        <div
          onClick={() => !isProcessing && fileInputRef.current?.click()}
          className={`border-2 border-dashed border-gray-300 rounded-lg p-8 text-center transition-colors ${
            isProcessing 
              ? 'opacity-50 cursor-not-allowed' 
              : 'hover:border-purple-400 cursor-pointer'
          }`}
        >
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
          </svg>
          <p className="text-sm text-gray-600 mb-2">
            Click to upload images (multiple selection supported)
          </p>
          <p className="text-xs text-gray-500">
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
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-700">Queue Status</h3>
            {isProcessing && (
              <div className="flex items-center text-purple-600">
                <ArrowPathIcon className="h-4 w-4 animate-spin mr-2" />
                <span className="text-xs font-medium">Processing...</span>
              </div>
            )}
          </div>
          <div className="grid grid-cols-4 gap-2 text-center text-xs">
            <div className="bg-gray-200 rounded px-2 py-1">
              <div className="font-semibold text-gray-700">{pendingCount}</div>
              <div className="text-gray-600">Pending</div>
            </div>
            <div className="bg-blue-100 rounded px-2 py-1">
              <div className="font-semibold text-blue-700">{processingCount}</div>
              <div className="text-blue-600">Processing</div>
            </div>
            <div className="bg-green-100 rounded px-2 py-1">
              <div className="font-semibold text-green-700">{completedCount}</div>
              <div className="text-green-600">Completed</div>
            </div>
            <div className="bg-red-100 rounded px-2 py-1">
              <div className="font-semibold text-red-700">{errorCount}</div>
              <div className="text-red-600">Failed</div>
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
              className={`border rounded-lg p-3 flex items-center space-x-3 ${
                item.status === 'processing' ? 'border-purple-300 bg-purple-50' :
                item.status === 'completed' ? 'border-green-300 bg-green-50' :
                item.status === 'error' ? 'border-red-300 bg-red-50' :
                'border-gray-200 bg-white'
              }`}
            >
              {/* Thumbnail */}
              <div className="w-16 h-16 flex-shrink-0 relative bg-gray-100 rounded overflow-hidden">
                <img
                  src={item.preview}
                  alt="Preview"
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs font-medium text-gray-700 truncate">
                    {item.file.name}
                  </p>
                  <div className="flex items-center space-x-1 ml-2">
                    {item.status === 'pending' && (
                      <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-200 rounded">
                        Pending
                      </span>
                    )}
                    {item.status === 'processing' && (
                      <span className="text-xs text-purple-600 px-2 py-0.5 bg-purple-200 rounded flex items-center">
                        <ArrowPathIcon className="h-3 w-3 animate-spin mr-1" />
                        Processing
                      </span>
                    )}
                    {item.status === 'completed' && (
                      <span className="text-xs text-green-600 px-2 py-0.5 bg-green-200 rounded flex items-center">
                        <CheckCircleIcon className="h-3 w-3 mr-1" />
                        Done
                      </span>
                    )}
                    {item.status === 'error' && (
                      <span className="text-xs text-red-600 px-2 py-0.5 bg-red-200 rounded flex items-center">
                        <ExclamationCircleIcon className="h-3 w-3 mr-1" />
                        Failed
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {item.style} · {item.detailLevel}
                </div>
                {item.error && (
                  <div className="text-xs text-red-600 mt-1 truncate">
                    {item.error}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-1">
                {item.status === 'error' && (
                  <button
                    onClick={() => retryItem(item.id)}
                    className="p-1 text-blue-600 hover:text-blue-700 rounded hover:bg-blue-100"
                    title="Retry"
                  >
                    <ArrowPathIcon className="h-4 w-4" />
                  </button>
                )}
                {(item.status === 'pending' || item.status === 'error' || item.status === 'completed') && (
                  <button
                    onClick={() => removeFromQueue(item.id)}
                    disabled={item.status === 'processing'}
                    className="p-1 text-red-600 hover:text-red-700 rounded hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Remove"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {queue.length === 0 && (
        <div className="text-center py-8 text-gray-500 text-sm">
          No images in queue. Upload images to get started!
        </div>
      )}
    </div>
  )
}
