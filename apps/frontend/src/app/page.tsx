'use client'

import { useState } from 'react'
import { 
  PhotoIcon, 
  SparklesIcon, 
  ListBulletIcon, 
  ChartBarIcon
} from '@heroicons/react/24/outline'
import ImageGenerationForm from '@/components/ImageGenerationForm'
import GeneratedImages from '@/components/GeneratedImages'
import PromptsDisplay from '@/components/PromptsDisplay'
import AnalyticsDashboard from '@/components/AnalyticsDashboard'

export default function Home() {
  const [images, setImages] = useState<any[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeTab, setActiveTab] = useState<'generate' | 'prompts' | 'analytics'>('generate')

  const handleImageGenerated = (newImage: any) => {
    setImages(prev => [newImage, ...prev])
  }

  const handlePromptSelect = (prompt: string) => {
    // Switch to generate tab and set the prompt
    setActiveTab('generate')
    // You could pass this to the form component via props
    console.log('Selected prompt:', prompt)
  }

  const navigation = [
    { name: 'Generate', id: 'generate', icon: SparklesIcon, current: activeTab === 'generate' },
    { name: 'Prompts', id: 'prompts', icon: ListBulletIcon, current: activeTab === 'prompts' },
    { name: 'Analytics', id: 'analytics', icon: ChartBarIcon, current: activeTab === 'analytics' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Navigation */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-primary-600 to-blue-600 p-2 rounded-lg">
                <SparklesIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ImageGenAI</h1>
                <p className="text-xs text-gray-500">AI-Powered Image Generation</p>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="hidden md:flex space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.name}
                    onClick={() => setActiveTab(item.id as any)}
                    className={`nav-tab ${
                      item.current ? 'nav-tab-active' : 'nav-tab-inactive'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </button>
                )
              })}
            </nav>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <select
                value={activeTab}
                onChange={(e) => setActiveTab(e.target.value as any)}
                className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
              >
                {navigation.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>

          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {/* Tab Content */}
        {activeTab === 'generate' && (
          <div className="py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
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
          </div>
        )}

        {activeTab === 'prompts' && (
          <div className="py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
              <PromptsDisplay onPromptSelect={handlePromptSelect} />
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
              <AnalyticsDashboard />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="bg-gradient-to-r from-primary-600 to-blue-600 p-1 rounded">
                <SparklesIcon className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm text-gray-600">ImageGenAI</span>
            </div>
            <div className="text-sm text-gray-500">
              © 2024 ImageGenAI. Built with FastAPI and Next.js
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
