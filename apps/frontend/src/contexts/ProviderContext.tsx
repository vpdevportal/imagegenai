'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type AIProvider = 'gemini' | 'replicate' | 'stability' | 'huggingface'

interface ProviderContextType {
  provider: AIProvider
  setProvider: (provider: AIProvider) => void
  availableProviders: AIProvider[]
}

const ProviderContext = createContext<ProviderContextType | undefined>(undefined)

const STORAGE_KEY = 'imagegenai_ai_provider'
const DEFAULT_PROVIDER: AIProvider = 'gemini'
const AVAILABLE_PROVIDERS: AIProvider[] = ['gemini', 'replicate', 'stability', 'huggingface']

export function ProviderProvider({ children }: { children: ReactNode }) {
  const [provider, setProviderState] = useState<AIProvider>(DEFAULT_PROVIDER)
  const [isInitialized, setIsInitialized] = useState(false)

  // Load provider from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY) as AIProvider | null
      if (stored && AVAILABLE_PROVIDERS.includes(stored)) {
        setProviderState(stored)
      }
      setIsInitialized(true)
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

  // Don't render children until initialized to avoid hydration mismatch
  if (!isInitialized) {
    return null
  }

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
  if (context === undefined) {
    throw new Error('useProvider must be used within a ProviderProvider')
  }
  return context
}

