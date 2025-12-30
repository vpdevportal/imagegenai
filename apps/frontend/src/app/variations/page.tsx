import VariationsPageClient from './VariationsPageClient'

// Force dynamic rendering - this is a server component wrapper
export const dynamic = 'force-dynamic'

export default function VariationsPage() {
  return <VariationsPageClient />
}

