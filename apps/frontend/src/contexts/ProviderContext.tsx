'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type AIProvider = 'gemini' | 'replicate' | 'stability'

interface ProviderContextType {
  provider: AIProvider
  setProvider: (provider: AIProvider) => void
  availableProviders: AIProvider[]
}

const STORAGE_KEY = 'imagegenai_ai_provider'
const DEFAULT_PROVIDER: AIProvider = 'gemini'
const AVAILABLE_PROVIDERS: AIProvider[] = ['gemini', 'replicate', 'stability']

// Create context with default value to avoid undefined during SSR
const ProviderContext = createContext<ProviderContextType>({
  provider: DEFAULT_PROVIDER,
  setProvider: () => {},
  availableProviders: AVAILABLE_PROVIDERS,
})

export function ProviderProvider({ children }: { children: ReactNode }) {
  // Initialize with default provider immediately (works for SSR/SSG)
  const [provider, setProviderState] = useState<AIProvider>(DEFAULT_PROVIDER)
  const [isMounted, setIsMounted] = useState(false)

  // Load provider from localStorage after mount (client-side only)
  useEffect(() => {
    setIsMounted(true)
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY) as AIProvider | null
      if (stored && AVAILABLE_PROVIDERS.includes(stored)) {
        setProviderState(stored)
      }
    }
  }, [])

  // Save provider to localStorage when it changes
  const setProvider = (newProvider: AIProvider) => {
    if (AVAILABLE_PROVIDERS.includes(newProvider)) {
      setProviderState(newProvider)
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, newProvider)
      }
    }
  }

  // Always provide context value (never return null)
  return (
    <ProviderContext.Provider
      value={{
        provider,
        setProvider,
        availableProviders: AVAILABLE_PROVIDERS,
      }}
    >
      {children}
    </ProviderContext.Provider>
  )
}

export function useProvider() {
  const context = useContext(ProviderContext)
  // Context always has a value (default or from provider), so no need to check
  return context
}

