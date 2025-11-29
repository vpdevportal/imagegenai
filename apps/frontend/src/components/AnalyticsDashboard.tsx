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
import { getPromptStats } from '@/services/api'
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
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-400 mb-2 font-medium">{error}</div>
        <button
          onClick={loadStats}
          className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
        >
          Try again
        </button>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <div className="bg-gradient-to-r from-indigo-900/50 to-purple-900/50 p-6 rounded-2xl w-24 h-24 mx-auto mb-4 flex items-center justify-center shadow-lg">
          <ChartBarIcon className="h-12 w-12 text-indigo-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-200 mb-2">No Data Available</h3>
        <p className="text-gray-400">Start generating images to see analytics</p>
      </div>
    )
  }

  const metrics = [
    {
      name: 'Total Prompts',
      value: stats.total_prompts,
      icon: ChartBarIcon,
      color: 'text-blue-400',
      bgColor: 'bg-blue-900/30',
      change: '+12%',
      changeType: 'positive' as const
    },
    {
      name: 'Total Uses',
      value: stats.total_uses,
      icon: FireIcon,
      color: 'text-orange-400',
      bgColor: 'bg-orange-900/30',
      change: '+8%',
      changeType: 'positive' as const
    },
    {
      name: 'With Thumbnails',
      value: stats.prompts_with_thumbnails,
      icon: EyeIcon,
      color: 'text-green-400',
      bgColor: 'bg-green-900/30',
      change: '+15%',
      changeType: 'positive' as const
    },
    {
      name: 'Most Popular',
      value: stats.most_popular_uses,
      icon: ArrowTrendingUpIcon,
      color: 'text-purple-400',
      bgColor: 'bg-purple-900/30',
      change: '+5%',
      changeType: 'positive' as const
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text">Analytics Dashboard</h2>
          <p className="text-gray-300 font-medium">Overview of your prompt usage and performance</p>
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
                  <p className="text-sm font-medium text-gray-400">{metric.name}</p>
                  <p className="text-2xl font-bold text-gray-200">{metric.value.toLocaleString()}</p>
                </div>
                <div className={`p-3 rounded-xl ${metric.bgColor} border border-gray-700/50`}>
                  <Icon className={`h-6 w-6 ${metric.color}`} />
                </div>
              </div>
              <div className="mt-4 flex items-center">
                {metric.changeType === 'positive' ? (
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-400 mr-1" />
                ) : (
                  <ArrowTrendingDownIcon className="h-4 w-4 text-red-400 mr-1" />
                )}
                <span className={`text-sm font-medium ${
                  metric.changeType === 'positive' ? 'text-green-400' : 'text-red-400'
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
          <h3 className="text-lg font-semibold text-gray-200 mb-4">Most Popular Prompt</h3>
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700/50">
            <p className="text-gray-200 mb-2 font-medium">{stats.most_popular_prompt}</p>
            <div className="flex items-center text-sm text-gray-400">
              <FireIcon className="h-4 w-4 mr-1 text-orange-400" />
              <span>{stats.most_popular_uses} uses</span>
            </div>
          </div>
        </div>
      )}

      {/* Usage Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-200 mb-4">Usage Insights</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Average uses per prompt</span>
              <span className="font-medium text-gray-200">
                {stats.total_prompts > 0 ? (stats.total_uses / stats.total_prompts).toFixed(1) : 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Thumbnail coverage</span>
              <span className="font-medium text-gray-200">
                {stats.total_prompts > 0 ? ((stats.prompts_with_thumbnails / stats.total_prompts) * 100).toFixed(1) : 0}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Most used prompt</span>
              <span className="font-medium text-gray-200">
                {stats.most_popular_uses} times
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-200 mb-4">Quick Actions</h3>
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
