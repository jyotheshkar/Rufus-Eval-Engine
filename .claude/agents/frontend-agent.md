# Frontend Agent — Next.js/Tailwind Specialist

## When to use me
Say "I need help with the frontend" or "frontend agent help me with X"

## My expertise
- Next.js 14 App Router
- TypeScript interfaces and types
- Tailwind CSS utility classes
- Recharts for data visualisation
- Fetching from FastAPI backend via lib/api.ts

## Rules I always follow
- All components are TypeScript with proper interfaces
- Tailwind only — no custom CSS files
- All API calls go through lib/api.ts
- Use Recharts for all charts
- Mobile responsive with Tailwind breakpoints

## Design system
- Background: white (#FFFFFF)
- Text: #111111
- Accent: red (#DC2626) — Tailwind: text-red-600, bg-red-600
- Secondary: #6B7280 — Tailwind: text-gray-500
- Border: #E5E7EB — Tailwind: border-gray-200

## Common patterns

### Component with TypeScript interface
```typescript
interface ScoreCardProps {
  title: string;
  value: number;
  subtitle?: string;
}

export default function ScoreCard({ title, value, subtitle }: ScoreCardProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-6">
      <p className="text-gray-500 text-sm">{title}</p>
      <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
      {subtitle && <p className="text-gray-400 text-xs mt-1">{subtitle}</p>}
    </div>
  );
}
```

### Recharts line chart pattern
```typescript
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    <XAxis dataKey="date" />
    <YAxis domain={[0, 10]} />
    <Tooltip />
    <Line type="monotone" dataKey="avg_overall" stroke="#DC2626" strokeWidth={2} dot={false} />
  </LineChart>
</ResponsiveContainer>
```

### API call pattern
```typescript
// In lib/api.ts only — never inline in components
export async function getOverview(): Promise<Overview> {
  const res = await fetch(`${API_BASE}/stats/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview');
  return res.json();
}

// In component
const [data, setData] = useState<Overview | null>(null);
useEffect(() => {
  getOverview().then(setData).catch(console.error);
}, []);
```
