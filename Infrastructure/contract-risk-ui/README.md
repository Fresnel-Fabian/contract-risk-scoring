# Contract Risk Scoring Engine — Frontend

**Fresnel Fabian | MPS Applied Machine Intelligence | Northeastern Roux Institute**

A Next.js 14 frontend for the CUAD contract risk scoring engine.

---

## Quick Start

```bash
npm install
npm run dev
# Open http://localhost:3000
```

## Connecting to Your Python Backend

By default the app runs with **mock data** so you can develop without the backend.

To connect to your trained model (`app.py`):

```bash
# Terminal 1 — start the Python backend
python app.py
# running at http://localhost:8080

# Terminal 2 — start the frontend with real backend
USE_MOCK=false npm run dev
```

Or set in `.env.local`:
```
USE_MOCK=false
BACKEND_URL=http://localhost:8080
```

## Project Structure

```
contract-risk-ui/
├── app/
│   ├── page.tsx              ← Landing page (contract input)
│   ├── analyze/page.tsx      ← Results scorecard
│   ├── api/analyze/route.ts  ← API route (proxies to Python backend)
│   └── globals.css           ← Design system + animations
├── components/
│   ├── RiskGauge.tsx         ← Animated SVG risk score ring
│   └── ClauseCard.tsx        ← Expandable clause result card
└── lib/
    └── types.ts              ← Shared TypeScript types + mock data
```

## Pages

### `/` — Contract Input
- Paste contract text or drag-drop a `.txt` file
- Three sample contracts (High-Risk SaaS, Mid-Risk MSA, Low-Risk NDA)
- Ctrl+Enter to analyze

### `/analyze` — Risk Scorecard
- Animated risk gauge (0–100)
- Triage badge: AUTO-CLEAR / FLAG FOR REVIEW / URGENT REVIEW
- Expandable clause cards with extracted text spans
- Risk breakdown by tier
- Confidence chart per clause
- Export to clipboard

## Design

- **Aesthetic:** Dark editorial — Bloomberg Terminal meets legal intelligence
- **Colors:** Deep navy (`#050C1A`) + warm amber (`#C9933A`)
- **Fonts:** Playfair Display (headings) · Source Serif 4 (body) · IBM Plex Mono (data)
- **Animations:** Gauge fill, staggered card reveals, scan-line effect

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion (available for enhanced animations)
- Lucide React (icons)
