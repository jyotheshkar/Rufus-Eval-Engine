// layout.tsx — root layout with Inter font and shared Nav
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Nav } from '@/components/Nav'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'Rufus Eval Engine',
  description: 'LLM evaluation dashboard for the Rufus AI shopping assistant',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans bg-[#f0f0f0] text-black min-h-screen antialiased`}>
        <Nav />
        <main>{children}</main>
      </body>
    </html>
  )
}
