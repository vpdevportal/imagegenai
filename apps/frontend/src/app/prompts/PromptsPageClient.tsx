'use client'

import PromptsDisplay from '@/components/PromptsDisplay'

export default function PromptsPageClient() {
  const handlePromptSelect = (promptId: number, type: 'generate' | 'group') => {
    const path = type === 'group' ? `/grouping?promptId=${promptId}` : `/generate?promptId=${promptId}`
    window.open(path, '_blank', 'noopener,noreferrer')
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <PromptsDisplay onPromptSelect={handlePromptSelect} />
      </div>
    </div>
  )
}

