# Sales Best Friend — Design & Development Rules

## Design System

This is a **B2B SaaS product** for sales team managers. The design must feel like Linear, Notion, or Vercel Dashboard — clean, minimal, functional. Never generic "AI slop."

### Typography
- **Primary font**: `Inter` for UI text (it's actually appropriate here — this is a data-heavy SaaS tool)
- **Monospace**: `JetBrains Mono` for timestamps, scores, code-like data
- **Heading hierarchy**: Use font-weight contrast (400 vs 600) more than size. Max 3 heading sizes per page.
- **Body text**: 14px (text-sm) is the default. 13px (text-xs) for secondary. 16px (text-base) for emphasis only.
- No decorative fonts. No serif fonts. No all-caps headings.

### Colors
- **Background**: `#FAFAFA` (gray-50) for page, `#FFFFFF` for cards
- **Text primary**: `#0F172A` (slate-900)
- **Text secondary**: `#64748B` (slate-500)
- **Text muted**: `#94A3B8` (slate-400)
- **Border**: `#E2E8F0` (slate-200), use sparingly
- **Accent (primary)**: `#2563EB` (blue-600) — used for primary actions, links, active states
- **Success**: `#10B981` (emerald-500) — completed items, positive scores
- **Warning**: `#F59E0B` (amber-500) — slightly late, medium scores
- **Danger**: `#EF4444` (red-500) — very late, low scores, errors
- **Score heatmap**: green (#10B981) → yellow (#F59E0B) → red (#EF4444) for score cells

### Spacing & Layout
- **Sidebar**: 240px wide, dark (slate-900 background, white text)
- **Content area**: max-width 1400px, centered, with 24px padding
- **Card spacing**: 16px padding inside, 16px gap between cards
- **Section spacing**: 32px between major sections
- **Table row height**: 48px minimum
- **Border radius**: `rounded-lg` (8px) for cards, `rounded-md` (6px) for buttons/inputs

### Components Style Guide
- **Cards**: White background, 1px border (slate-200), subtle shadow (`shadow-sm`). No heavy shadows.
- **Buttons**: Primary = blue-600 filled. Secondary = ghost/outline. Size = `h-9 px-4` default. Never rounded-full.
- **Tables**: Clean rows with hover state (slate-50). No zebra stripes. Thin bottom border per row.
- **Badges/Tags**: Small rounded pills. Use colored dot + text, not fully colored background. See screenshot reference.
- **Modals**: Clean, max-width 480px for forms, 640px for content. Subtle overlay.
- **Inputs**: Height 36px, 1px border, focus ring blue-600.
- **Empty states**: Icon + short text + action button. Never just text.
- **Loading**: Use skeleton placeholders (shadcn Skeleton), never spinners.

### Patterns to AVOID
- No gradient backgrounds on cards or sections
- No heavy box shadows (drop-shadow-xl etc.)
- No decorative illustrations or mascots
- No animated backgrounds or particles
- No rounded-full buttons (except icon-only small buttons)
- No emoji in UI labels (emoji OK in user content like chat)
- No purple/pink accent colors (this is a professional B2B tool)
- No card elevation hierarchy (flat design with borders)

### Responsive
- Desktop-first. Sidebar collapses to icons on < 1024px.
- Tables become card-based lists on mobile.
- Live call page is desktop-only (complex multi-panel layout).

## Code Conventions

### Frontend (React + TypeScript)
- **State management**: TanStack Query for server state, Zustand for client-only state
- **API calls**: All through `lib/api.ts` using fetch with auth headers
- **Supabase**: Use `@supabase/supabase-js` client for auth, storage, and realtime subscriptions only
- **Components**: Functional components with hooks. No class components.
- **File naming**: PascalCase for components (`CallsTable.tsx`), camelCase for hooks (`useCalls.ts`), lowercase for lib (`api.ts`)
- **Imports**: Absolute imports via `@/` alias (e.g., `@/components/ui/button`)
- **No prop drilling**: Use Zustand stores or React Context for shared state across 3+ levels

### Backend (Python + FastAPI)
- **Structure**: Feature-based modules under `app/api/v1/endpoints/`
- **Database**: Supabase Python client (`supabase-py`) for CRUD
- **Auth**: Validate Supabase JWT in middleware, extract user_id
- **AI calls**: All through `services/llm/base.py` OpenRouter client
- **WebSocket**: Per-call connections keyed by call_id in `websocket/manager.py`
- **Error handling**: HTTPException with proper status codes, structured error responses

### Git
- Conventional commits: `feat:`, `fix:`, `refactor:`, `chore:`
- Feature branches: `feature/phase-1-foundation`, etc.
