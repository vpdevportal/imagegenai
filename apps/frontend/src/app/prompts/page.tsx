'use client'

import { useRouter } from 'next/navigation'
import PromptsDisplay from '@/components/PromptsDisplay'

export default function PromptsPage() {
  const router = useRouter()

  const handlePromptSelect = (promptId: number, type: 'generate' | 'group') => {
    // Navigate to the appropriate page with the selected prompt ID as URL parameter
    if (type === 'group') {
      router.push(`/grouping?promptId=${promptId}`)
    } else {
      router.push(`/generate?promptId=${promptId}`)
    }
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <PromptsDisplay onPromptSelect={handlePromptSelect} />
      </div>
    </div>
  )
}
