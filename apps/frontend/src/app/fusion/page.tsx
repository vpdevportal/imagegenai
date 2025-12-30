import FusionPageClient from './FusionPageClient'

// Force dynamic rendering - this is a server component wrapper
export const dynamic = 'force-dynamic'

export default function FusionPage() {
  return <FusionPageClient />
}

