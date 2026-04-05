// Nav — shared top navigation bar for all dashboard screens
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const LINKS = [
  { href: '/', label: 'Overview' },
  { href: '/feed', label: 'Answer Feed' },
  { href: '/analysis', label: 'Weak Spots' },
  { href: '/adversarial', label: 'Adversarial' },
  { href: '/dataset', label: 'Visualise Dataset' },
]

export function Nav() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center h-12">
          <span className="font-semibold text-sm text-black tracking-tight">
            Rufus Eval Engine
          </span>

          <nav className="flex items-center gap-6 ml-auto">
            {LINKS.map(({ href, label }) => {
              const active = pathname === href
              return (
                <Link
                  key={href}
                  href={href}
                  className={`text-[13px] py-3 border-b-2 transition-colors ${
                    active
                      ? 'border-black text-black font-medium'
                      : 'border-transparent text-gray-400 hover:text-black'
                  }`}
                >
                  {label}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}
