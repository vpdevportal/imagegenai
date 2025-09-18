'use client'

import { useState, useEffect } from 'react'
import { 
  ChartBarIcon, 
  FireIcon, 
  ClockIcon, 
  EyeIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'
import { getPromptStats } from '@/lib/api'
import { PromptStats } from '@/types'

export default function AnalyticsDashboard() {
  const [stats, setStats] = useState<PromptStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const statsData = await getPromptStats()
      setStats(statsData)
    } catch (err) {
      setError('Failed to load analytics data')
      console.error('Error loading stats:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-2">{error}</div>
        <button
          onClick={loadStats}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          Try again
        </button>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
        <p className="text-gray-500">Start generating images to see analytics</p>
      </div>
    )
  }

  const metrics = [
    {
      name: 'Total Prompts',
      value: stats.total_prompts,
      icon: ChartBarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      change: '+12%',
      changeType: 'positive' as const
    },
    {
      name: 'Total Uses',
      value: stats.total_uses,
      icon: FireIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      change: '+8%',
      changeType: 'positive' as const
    },
    {
      name: 'With Thumbnails',
      value: stats.prompts_with_thumbnails,
      icon: EyeIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: '+15%',
      changeType: 'positive' as const
    },
    {
      name: 'Most Popular',
      value: stats.most_popular_uses,
      icon: ArrowTrendingUpIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      change: '+5%',
      changeType: 'positive' as const
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600">Overview of your prompt usage and performance</p>
        </div>
        <button
          onClick={loadStats}
          className="btn-secondary flex items-center"
        >
          <ClockIcon className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <div key={metric.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{metric.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{metric.value.toLocaleString()}</p>
                </div>
                <div className={`p-3 rounded-lg ${metric.bgColor}`}>
                  <Icon className={`h-6 w-6 ${metric.color}`} />
                </div>
              </div>
              <div className="mt-4 flex items-center">
                {metric.changeType === 'positive' ? (
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                ) : (
                  <ArrowTrendingDownIcon className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm font-medium ${
                  metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {metric.change}
                </span>
                <span className="text-sm text-gray-500 ml-1">from last month</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Most Popular Prompt */}
      {stats.most_popular_prompt && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Popular Prompt</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-800 mb-2">{stats.most_popular_prompt}</p>
            <div className="flex items-center text-sm text-gray-600">
              <FireIcon className="h-4 w-4 mr-1" />
              <span>{stats.most_popular_uses} uses</span>
            </div>
          </div>
        </div>
      )}

      {/* Usage Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Insights</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Average uses per prompt</span>
              <span className="font-medium">
                {stats.total_prompts > 0 ? (stats.total_uses / stats.total_prompts).toFixed(1) : 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Thumbnail coverage</span>
              <span className="font-medium">
                {stats.total_prompts > 0 ? ((stats.prompts_with_thumbnails / stats.total_prompts) * 100).toFixed(1) : 0}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Most used prompt</span>
              <span className="font-medium">
                {stats.most_popular_uses} times
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full btn-secondary text-left">
              Export prompt data
            </button>
            <button className="w-full btn-secondary text-left">
              View detailed reports
            </button>
            <button className="w-full btn-secondary text-left">
              Manage prompts
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
