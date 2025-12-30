import PromptsPageClient from './PromptsPageClient'

// Force dynamic rendering - this is a server component wrapper
export const dynamic = 'force-dynamic'

export default function PromptsPage() {
  return <PromptsPageClient />
}
