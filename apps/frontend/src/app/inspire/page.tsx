import InspirePageClient from './InspirePageClient'

// Force dynamic rendering - this is a server component wrapper
export const dynamic = 'force-dynamic'

export default function InspirePage() {
  return <InspirePageClient />
}
