'use client'

import { useState, useEffect, useCallback } from 'react'
import { 
  MagnifyingGlassIcon, 
  FireIcon, 
  ClockIcon, 
  EyeIcon,
  ChartBarIcon,
  XMarkIcon,
  TrashIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import Image from 'next/image'
import { 
  getPrompts, 
  getPopularPrompts, 
  getRecentPrompts, 
  getMostFailedPrompts,
  searchPrompts, 
  getPromptStats,
  getPromptThumbnail,
  deletePrompt
} from '@/lib/api'
import { Prompt, PromptStats, PromptListResponse } from '@/types'
import ConfirmationDialog from './ConfirmationDialog'
import { useToast } from '@/contexts/ToastContext'

interface PromptsDisplayProps {
  onPromptSelect?: (prompt: string) => void
}

export default function PromptsDisplay({ onPromptSelect }: PromptsDisplayProps) {
  const { addToast } = useToast()
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [stats, setStats] = useState<PromptStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'recent' | 'popular' | 'most-failed' | 'search'>('recent')
  const [thumbnails, setThumbnails] = useState<Record<number, string>>({})
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set())
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const [itemsPerPage] = useState(21) // Smaller page size for better UX
  const [allPrompts, setAllPrompts] = useState<Prompt[]>([]) // Store all fetched prompts
  const [confirmationDialog, setConfirmationDialog] = useState<{
    isOpen: boolean
    promptId: number | null
    promptText: string
  }>({
    isOpen: false,
    promptId: null,
    promptText: ''
  })

  const loadPrompts = useCallback(async (tab: 'recent' | 'popular' | 'most-failed' | 'search' = 'recent') => {
    setLoading(true)
    setError('')
    
    try {
      let fetchedPrompts: Prompt[] = []
      
      if (tab === 'recent') {
        fetchedPrompts = await getRecentPrompts(100) // Fetch more data for client-side pagination
      } else if (tab === 'popular') {
        fetchedPrompts = await getPopularPrompts(100) // Fetch more data for client-side pagination
      } else if (tab === 'most-failed') {
        fetchedPrompts = await getMostFailedPrompts(100) // Fetch more data for client-side pagination
      } else if (tab === 'search' && searchQuery.trim()) {
        fetchedPrompts = await searchPrompts(searchQuery.trim(), 100) // Fetch more data for client-side pagination
      }
      
      setAllPrompts(fetchedPrompts)
      setTotalItems(fetchedPrompts.length)
      setTotalPages(Math.ceil(fetchedPrompts.length / itemsPerPage))
      setCurrentPage(1) // Reset to first page when loading new data
      
      // Load thumbnails for all fetched prompts
      const thumbnailPromises = fetchedPrompts
        .filter(prompt => prompt.thumbnail_mime)
        .map(async (prompt) => {
          try {
            const thumbnailUrl = await getPromptThumbnail(prompt.id)
            return { id: prompt.id, url: thumbnailUrl }
          } catch (err) {
            console.warn(`Failed to load thumbnail for prompt ${prompt.id}:`, err)
            return null
          }
        })
      
      const thumbnailResults = await Promise.all(thumbnailPromises)
      const thumbnailMap: Record<number, string> = {}
      thumbnailResults.forEach(result => {
        if (result) {
          thumbnailMap[result.id] = result.url
        }
      })
      setThumbnails(thumbnailMap)
      
    } catch (err) {
      setError('Failed to load prompts')
      console.error('Error loading prompts:', err)
    } finally {
      setLoading(false)
    }
  }, [searchQuery, itemsPerPage])

  // Update displayed prompts based on current page
  useEffect(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    const pagePrompts = allPrompts.slice(startIndex, endIndex)
    setPrompts(pagePrompts)
  }, [allPrompts, currentPage, itemsPerPage])

  const loadStats = useCallback(async () => {
    try {
      const statsData = await getPromptStats()
      setStats(statsData)
    } catch (err) {
      console.error('Error loading stats:', err)
    }
  }, [])

  useEffect(() => {
    loadPrompts(activeTab)
    loadStats()
  }, [activeTab, loadPrompts, loadStats])

  useEffect(() => {
    if (activeTab === 'search' && searchQuery.trim()) {
      const timeoutId = setTimeout(() => {
        loadPrompts('search')
      }, 500)
      return () => clearTimeout(timeoutId)
    }
  }, [searchQuery, activeTab, loadPrompts])

  // Handle page changes (client-side pagination)
  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage)
      // No need to call loadPrompts again since we have all data
    }
  }

  const handlePromptClick = (prompt: Prompt) => {
    if (onPromptSelect) {
      onPromptSelect(prompt.prompt_text)
    }
  }

  const handleDeletePrompt = (promptId: number, event: React.MouseEvent) => {
    event.stopPropagation() // Prevent triggering the card click
    
    const prompt = prompts.find(p => p.id === promptId)
    if (prompt) {
      setConfirmationDialog({
        isOpen: true,
        promptId,
        promptText: prompt.prompt_text
      })
    }
  }

  const handleConfirmDelete = async () => {
    if (!confirmationDialog.promptId) return

    const promptId = confirmationDialog.promptId
    setDeletingIds(prev => new Set(prev).add(promptId))
    
    try {
      await deletePrompt(promptId)
      
      // Remove the prompt from the local state
      setPrompts(prev => prev.filter(p => p.id !== promptId))
      
      // Remove thumbnail from state
      setThumbnails(prev => {
        const newThumbnails = { ...prev }
        delete newThumbnails[promptId]
        return newThumbnails
      })
      
      // Reload stats to update counts
      loadStats()
      
      // Close confirmation dialog
      setConfirmationDialog({
        isOpen: false,
        promptId: null,
        promptText: ''
      })
      
    } catch (error) {
      console.error('Failed to delete prompt:', error)
      addToast({
        type: 'error',
        title: 'Delete Failed',
        message: 'Failed to delete prompt. Please try again.'
      })
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(promptId)
        return newSet
      })
    }
  }

  const handleCancelDelete = () => {
    setConfirmationDialog({
      isOpen: false,
      promptId: null,
      promptText: ''
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const clearSearch = () => {
    setSearchQuery('')
    setActiveTab('recent')
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      {stats && (
        <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <ChartBarIcon className="h-5 w-5 mr-2 text-primary-600" />
              Prompt Statistics
            </h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">{stats.total_prompts}</div>
              <div className="text-sm text-gray-600">Total Prompts</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.total_uses}</div>
              <div className="text-sm text-gray-600">Total Uses</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.total_fails}</div>
              <div className="text-sm text-gray-600">Total Failures</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.prompts_with_thumbnails}</div>
              <div className="text-sm text-gray-600">With Thumbnails</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.most_popular_uses}</div>
              <div className="text-sm text-gray-600">Most Popular Uses</div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Tabs */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              if (e.target.value.trim()) {
                setActiveTab('search')
              }
            }}
            className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          {searchQuery && (
            <button
              onClick={clearSearch}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('recent')}
            className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'recent'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <ClockIcon className="h-4 w-4 mr-2" />
            Recent
          </button>
          <button
            onClick={() => setActiveTab('popular')}
            className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'popular'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FireIcon className="h-4 w-4 mr-2" />
            Popular
          </button>
          <button
            onClick={() => setActiveTab('most-failed')}
            className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'most-failed'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <ExclamationTriangleIcon className="h-4 w-4 mr-2" />
            Most Failed
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'search'
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
            Search
          </button>
        </div>
      </div>

      {/* Prompts Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <div className="text-red-600 mb-2">{error}</div>
          <button
            onClick={() => loadPrompts(activeTab)}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Try again
          </button>
        </div>
      ) : prompts.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-2">
            {activeTab === 'search' ? 'No prompts found' : 
             activeTab === 'most-failed' ? 'No failed prompts found' : 
             'No prompts available'}
          </div>
          {activeTab === 'search' && (
            <button
              onClick={clearSearch}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear search
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {prompts.map((prompt) => (
            <div
              key={prompt.id}
              onClick={() => handlePromptClick(prompt)}
              className="bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all cursor-pointer group flex h-20 overflow-hidden"
            >
              {/* Thumbnail */}
              <div className="w-20 h-20 flex-shrink-0 relative bg-gray-100 rounded-l-lg overflow-hidden border-r border-gray-200">
                {thumbnails[prompt.id] ? (
                  <Image
                    src={thumbnails[prompt.id]}
                    alt="Prompt thumbnail"
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-200"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <EyeIcon className="h-5 w-5" />
                  </div>
                )}
                
                {/* Overlay with usage count */}
                <div className="absolute top-1 right-1 bg-black/70 text-white text-xs px-1 py-0.5 rounded-full">
                  {prompt.total_uses}
                </div>
                
                {/* Failure count overlay */}
                {prompt.total_fails > 0 && (
                  <div className="absolute bottom-1 left-1 bg-red-600/80 text-white text-xs px-1 py-0.5 rounded-full">
                    {prompt.total_fails}
                  </div>
                )}
              </div>
              
              {/* Content */}
              <div className="flex-1 px-3 py-2 flex flex-col justify-between">
                <p className="text-xs text-gray-900 line-clamp-2 leading-tight">
                  {prompt.prompt_text}
                </p>
                <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                  <span>{formatDate(prompt.last_used_at)}</span>
                  <div className="flex items-center space-x-2">
                    {prompt.model && (
                      <span className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">
                        {prompt.model}
                      </span>
                    )}
                    <button
                      onClick={(e) => handleDeletePrompt(prompt.id, e)}
                      disabled={deletingIds.has(prompt.id)}
                      className="text-red-400 hover:text-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      title="Delete prompt"
                    >
                      {deletingIds.has(prompt.id) ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-400"></div>
                      ) : (
                        <TrashIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {!loading && !error && prompts.length > 0 && totalPages > 1 && (
        <div className="flex items-center justify-between mt-6 px-4 py-3 bg-gray-50 rounded-lg">
          <div className="flex items-center text-sm text-gray-700">
            <span>
              Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} prompts
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Previous Button */}
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
            >
              Previous
            </button>
            
            {/* Page Numbers */}
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum: number
                if (totalPages <= 5) {
                  pageNum = i + 1
                } else if (currentPage <= 3) {
                  pageNum = i + 1
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i
                } else {
                  pageNum = currentPage - 2 + i
                }
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum)}
                    className={`px-3 py-1 text-sm font-medium rounded-md ${
                      currentPage === pageNum
                        ? 'bg-primary-600 text-white'
                        : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>
            
            {/* Next Button */}
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={confirmationDialog.isOpen}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="Delete Prompt"
        message={`Are you sure you want to delete this prompt? This action cannot be undone.

"${confirmationDialog.promptText.length > 100 ? confirmationDialog.promptText.substring(0, 100) + '...' : confirmationDialog.promptText}"`}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
        isLoading={confirmationDialog.promptId ? deletingIds.has(confirmationDialog.promptId) : false}
      />
    </div>
  )
}
