# Code Style — Rufus Eval Engine

## Python (backend/)

- Python 3.11+; type hints on every function signature
- All FastAPI routes use `async def`
- All models inherit from `pydantic.BaseModel`
- Environment variables loaded via `python-dotenv` — never hardcoded
- All API calls wrapped in `try/except` with structured error responses
- One function, one job — keep functions small and focused
- Every file starts with a one-line comment explaining what it does
- No `print()` in production code — use `logging` module
- Use `snake_case` for variables, functions, and filenames
- Use `PascalCase` for class names

## TypeScript (frontend/)

- TypeScript strict mode — no `any` types
- All components in `frontend/components/`; props interfaces defined above the component
- Named exports for all components (no default exports except pages and layouts)
- `"use client"` directive only when the component needs interactivity, browser APIs, or hooks
- All API calls go through `frontend/lib/api.ts` — never `fetch()` directly inside components
- Use Recharts for all charts — no other charting library
- Tailwind only for styling — no custom CSS files
- Use `cn()` from `lib/utils` for conditional class names
- No `console.log` in production code
- Use `camelCase` for variables and functions; `PascalCase` for components and types

## Both

- Every file gets a one-line comment at the top explaining its purpose
- No commented-out dead code committed to git
- Keep diffs small — one concern per commit
