import { Suspense } from 'react'
import GeneratePageClient from './GeneratePageClient'

// Force dynamic rendering - this is a server component wrapper
export const dynamic = 'force-dynamic'

export default function GeneratePage() {
  return (
    <Suspense fallback={<div className="flex justify-center items-center h-64"><div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div></div>}>
      <GeneratePageClient />
    </Suspense>
  )
}
