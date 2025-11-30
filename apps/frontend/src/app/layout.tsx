import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Layout from '@/components/Layout'
import { ToastProvider } from '@/contexts/ToastContext'
import { ToastContainer } from '@/components/Toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ImageGenAI - AI-Powered Image Generation',
  description: 'Generate stunning images using artificial intelligence',
  keywords: ['AI', 'image generation', 'artificial intelligence', 'creativity'],
  icons: {
    icon: '/icon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <ToastProvider>
          <Layout>
            {children}
          </Layout>
          <ToastContainer />
        </ToastProvider>
      </body>
    </html>
  )
}
