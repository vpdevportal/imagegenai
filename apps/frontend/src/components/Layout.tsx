'use client'

import { 
  SparklesIcon,
  ListBulletIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname()

  const navigation = [
    { name: 'Generate', href: '/generate', icon: SparklesIcon, current: pathname === '/generate' },
    { name: 'Prompts', href: '/prompts', icon: ListBulletIcon, current: pathname === '/prompts' },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, current: pathname === '/analytics' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header with Navigation */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/generate" className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-primary-600 to-blue-600 p-2 rounded-lg">
                <SparklesIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ImageGenAI</h1>
                <p className="text-xs text-gray-500">AI-Powered Image Generation</p>
              </div>
            </Link>

            {/* Navigation Tabs */}
            <nav className="hidden md:flex space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`nav-tab ${
                      item.current ? 'nav-tab-active' : 'nav-tab-inactive'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                )
              })}
            </nav>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <select
                value={pathname}
                onChange={(e) => window.location.href = e.target.value}
                className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
              >
                {navigation.map((item) => (
                  <option key={item.href} value={item.href}>
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
        {children}
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
