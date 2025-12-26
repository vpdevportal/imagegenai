// Prevent static generation - this route should be dynamic
export const dynamic = 'force-dynamic'
export const revalidate = 0

import Link from 'next/link'

export default function ErrorPage() {
  // This route should not be statically generated
  // Simple component to prevent Html import errors
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="text-center px-4">
        <h1 className="text-6xl font-bold text-white mb-4">500</h1>
        <h2 className="text-2xl text-gray-300 mb-4">Something went wrong!</h2>
        <p className="text-gray-400 mb-8">An error occurred while processing your request.</p>
        <Link
          href="/generate"
          className="inline-block px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg transition-colors"
        >
          Go to Home
        </Link>
      </div>
    </div>
  )
}

