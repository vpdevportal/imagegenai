'use client'

import {
  SparklesIcon,
  ListBulletIcon,
  LightBulbIcon,
  ArrowPathIcon,
  ArrowsRightLeftIcon,
  GlobeAmericasIcon,
  ChevronDownIcon,
  CpuChipIcon,
  ServerIcon,
  CloudIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'
import { Listbox, Transition } from '@headlessui/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useProvider } from '@/contexts/ProviderContext'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname()
  const { provider, setProvider, availableProviders } = useProvider()

  // Provider icons mapping
  const providerIcons = {
    gemini: SparklesIcon,
    replicate: CpuChipIcon,
    stability: ServerIcon,
  }

  const navigation = [
    { name: 'Generate', href: '/generate', icon: SparklesIcon, current: pathname === '/generate' },
    { name: 'Groupping', href: '/grouping', icon: UserGroupIcon, current: pathname === '/grouping' },
    { name: 'Variations', href: '/variations', icon: ArrowPathIcon, current: pathname === '/variations' },
    { name: 'Fusion', href: '/fusion', icon: ArrowsRightLeftIcon, current: pathname === '/fusion' },
    { name: 'Teleport', href: '/teleport', icon: GlobeAmericasIcon, current: pathname === '/teleport' },
    { name: 'Inspire', href: '/inspire', icon: LightBulbIcon, current: pathname === '/inspire' },
    { name: 'Prompts', href: '/prompts', icon: ListBulletIcon, current: pathname === '/prompts' },
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

            {/* Provider Selector and Mobile Menu */}
            <div className="flex items-center space-x-3">
              {/* Provider Dropdown - Desktop */}
              <div className="hidden md:block">
                <Listbox value={provider} onChange={setProvider}>
                  <div className="relative">
                    <Listbox.Button className="relative w-full min-w-[140px] cursor-pointer rounded-lg bg-[#1a1f2e] border border-[#2a3441] py-2 pl-3 pr-10 text-left text-sm text-gray-100 shadow-md focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 hover:border-teal-500/50 transition-all duration-200">
                      <span className="flex items-center truncate">
                        {(() => {
                          const Icon = providerIcons[provider as keyof typeof providerIcons] || SparklesIcon
                          return (
                            <>
                              <Icon className="h-4 w-4 mr-2 flex-shrink-0 text-teal-400" />
                              <span>{provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                            </>
                          )
                        })()}
                      </span>
                      <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                        <ChevronDownIcon className="h-4 w-4 text-gray-400" aria-hidden="true" />
                      </span>
                    </Listbox.Button>
                    <Transition
                      as="div"
                      leave="transition ease-in duration-100"
                      leaveFrom="opacity-100"
                      leaveTo="opacity-0"
                      className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-[#1a1f2e] border border-[#2a3441] py-1 text-sm shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                    >
                      <Listbox.Options>
                        {availableProviders.map((p) => {
                          const Icon = providerIcons[p as keyof typeof providerIcons] || SparklesIcon
                          return (
                            <Listbox.Option
                              key={p}
                              value={p}
                              className={({ active }) =>
                                `relative cursor-pointer select-none py-2 pl-3 pr-4 ${
                                  active ? 'bg-[#2a3441] text-teal-400' : 'text-gray-100'
                                }`
                              }
                            >
                              {({ selected }) => (
                                <div className="flex items-center">
                                  <Icon className="h-4 w-4 mr-2 flex-shrink-0 text-teal-400" />
                                  <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>
                                    {p.charAt(0).toUpperCase() + p.slice(1)}
                                  </span>
                                  {selected && (
                                    <span className="absolute inset-y-0 right-0 flex items-center pr-3 text-teal-400">
                                      <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                      </svg>
                                    </span>
                                  )}
                                </div>
                              )}
                            </Listbox.Option>
                          )
                        })}
                      </Listbox.Options>
                    </Transition>
                  </div>
                </Listbox>
              </div>

              {/* Mobile menu button */}
              <div className="md:hidden flex items-center space-x-2">
                <Listbox value={provider} onChange={setProvider}>
                  <div className="relative">
                    <Listbox.Button className="relative w-full min-w-[100px] cursor-pointer rounded-lg bg-[#1a1f2e] border border-[#2a3441] py-1.5 pl-2 pr-8 text-left text-xs text-gray-100 shadow-md focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500">
                      <span className="flex items-center truncate">
                        {(() => {
                          const Icon = providerIcons[provider as keyof typeof providerIcons] || SparklesIcon
                          return (
                            <>
                              <Icon className="h-3 w-3 mr-1.5 flex-shrink-0 text-teal-400" />
                              <span className="truncate">{provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                            </>
                          )
                        })()}
                      </span>
                      <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-1.5">
                        <ChevronDownIcon className="h-3 w-3 text-gray-400" aria-hidden="true" />
                      </span>
                    </Listbox.Button>
                    <Transition
                      as="div"
                      leave="transition ease-in duration-100"
                      leaveFrom="opacity-100"
                      leaveTo="opacity-0"
                      className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg bg-[#1a1f2e] border border-[#2a3441] py-1 text-xs shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                    >
                      <Listbox.Options>
                        {availableProviders.map((p) => {
                          const Icon = providerIcons[p as keyof typeof providerIcons] || SparklesIcon
                          return (
                            <Listbox.Option
                              key={p}
                              value={p}
                              className={({ active }) =>
                                `relative cursor-pointer select-none py-1.5 pl-2 pr-4 ${
                                  active ? 'bg-[#2a3441] text-teal-400' : 'text-gray-100'
                                }`
                              }
                            >
                              {({ selected }) => (
                                <div className="flex items-center">
                                  <Icon className="h-3 w-3 mr-1.5 flex-shrink-0 text-teal-400" />
                                  <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>
                                    {p.charAt(0).toUpperCase() + p.slice(1)}
                                  </span>
                                </div>
                              )}
                            </Listbox.Option>
                          )
                        })}
                      </Listbox.Options>
                    </Transition>
                  </div>
                </Listbox>
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
