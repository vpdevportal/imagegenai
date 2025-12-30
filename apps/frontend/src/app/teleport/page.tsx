import TeleportPageClient from './TeleportPageClient'

// Force dynamic rendering - this is a server component wrapper
export const dynamic = 'force-dynamic'

export default function TeleportPage() {
  return <TeleportPageClient />
}
