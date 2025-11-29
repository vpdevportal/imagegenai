'use client'

import {
  SparklesIcon,
  ListBulletIcon,
  ChartBarIcon,
  LightBulbIcon,
  ArrowPathIcon,
  ArrowsRightLeftIcon,
  GlobeAmericasIcon
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
    { name: 'Variations', href: '/variations', icon: ArrowPathIcon, current: pathname === '/variations' },
    { name: 'Fusion', href: '/fusion', icon: ArrowsRightLeftIcon, current: pathname === '/fusion' },
    { name: 'Teleport', href: '/teleport', icon: GlobeAmericasIcon, current: pathname === '/teleport' },
    { name: 'Inspire', href: '/inspire', icon: LightBulbIcon, current: pathname === '/inspire' },
    { name: 'Prompts', href: '/prompts', icon: ListBulletIcon, current: pathname === '/prompts' },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, current: pathname === '/analytics' },
  ]

  return (
    <div className="min-h-screen flex flex-col relative">
      {/* Header with Navigation */}
      <header className="glass-effect sticky top-0 z-40 border-b border-[#2a3441]/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/generate" className="flex items-center space-x-3 group">
              <div className="bg-gradient-to-r from-teal-500 to-cyan-600 p-2.5 rounded-lg shadow-md group-hover:shadow-lg transition-all duration-200">
                <SparklesIcon className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-100">ImageGenAI</h1>
                <p className="text-xs text-gray-500">AI-Powered Image Generation</p>
              </div>
            </Link>

            {/* Navigation Tabs */}
            <nav className="hidden md:flex space-x-2">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`nav-tab ${item.current ? 'nav-tab-active' : 'nav-tab-inactive'
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
                className="input-field text-sm"
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
      <main className="flex-1 relative z-10">
        {children}
      </main>

      {/* Footer */}
      <footer className="glass-effect border-t border-[#2a3441]/50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="bg-gradient-to-r from-teal-500 to-cyan-600 p-1.5 rounded">
                <SparklesIcon className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm text-gray-400">ImageGenAI</span>
            </div>
            <div className="text-sm text-gray-500">
              Powered by AI
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
