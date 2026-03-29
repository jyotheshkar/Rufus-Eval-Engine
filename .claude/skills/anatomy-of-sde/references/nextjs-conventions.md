# Next.js App Router Conventions

## File Conventions

| File | Purpose |
|---|---|
| `layout.tsx` | Shared UI wrapper, persists across routes |
| `page.tsx` | Unique UI for a route, makes route publicly accessible |
| `loading.tsx` | Loading UI with Suspense |
| `error.tsx` | Error boundary for route segment |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint |
| `middleware.ts` | Runs before request |

## Server vs Client Components

```tsx
// Server Component (default) — runs on server, no hooks
// Good for: data fetching, DB access, sensitive logic
export default async function Page() {
  const data = await fetch('...')
  return <div>{data}</div>
}

// Client Component — add directive at top
// Good for: interactivity, browser APIs, useState/useEffect
'use client'
import { useState } from 'react'
export function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

## Data Fetching Patterns

```tsx
// Server Component — direct async/await
async function ProductPage({ params }: { params: { id: string } }) {
  const product = await db.product.findUnique({ where: { id: params.id } })
  return <ProductCard product={product} />
}

// Client Component — Tanstack Query
'use client'
function ProductList() {
  const { data, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: () => fetch('/api/products').then(r => r.json())
  })
}
```

## Route Groups & Organization

```
app/
├── (marketing)/       ← route group, no URL segment
│   ├── about/page.tsx → /about
│   └── blog/page.tsx  → /blog
├── (app)/             ← authenticated area
│   ├── layout.tsx     ← auth check here
│   └── dashboard/page.tsx → /dashboard
└── api/
    └── products/route.ts → /api/products
```

## API Routes

```ts
// app/api/products/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const CreateProductSchema = z.object({
  name: z.string().min(1),
  price: z.number().positive(),
})

export async function POST(request: NextRequest) {
  const body = await request.json()
  const parsed = CreateProductSchema.safeParse(body)
  
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error }, { status: 400 })
  }
  
  const product = await db.product.create({ data: parsed.data })
  return NextResponse.json(product, { status: 201 })
}
```

## Metadata

```tsx
// Static
export const metadata = {
  title: 'My App',
  description: 'Description here',
}

// Dynamic
export async function generateMetadata({ params }) {
  const product = await getProduct(params.id)
  return { title: product.name }
}
```

## Environment Variables

```bash
# .env.local (never committed)
DATABASE_URL="..."
NEXTAUTH_SECRET="..."

# Public vars (exposed to browser)
NEXT_PUBLIC_API_URL="..."
```

Access: `process.env.DATABASE_URL` (server), `process.env.NEXT_PUBLIC_API_URL` (client + server)
