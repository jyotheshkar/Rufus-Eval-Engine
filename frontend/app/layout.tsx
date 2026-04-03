// layout.tsx — root Next.js layout with Tailwind and Inter font
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Rufus Eval Engine',
  description: 'LLM evaluation dashboard for the Rufus AI shopping assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-white text-gray-900 min-h-screen`}>
        {children}
      </body>
    </html>
  )
}
