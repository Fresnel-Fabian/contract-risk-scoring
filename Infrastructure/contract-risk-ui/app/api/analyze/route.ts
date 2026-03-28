import { NextRequest, NextResponse } from 'next/server'
import { MOCK_RESULT } from '@/lib/types'

// Set USE_MOCK=false and configure BACKEND_URL to use the real Python model
const USE_MOCK = process.env.USE_MOCK !== 'false'
const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8080'

export async function POST(req: NextRequest) {
  try {
    const { text } = await req.json()

    if (!text || typeof text !== 'string' || text.trim().length < 20) {
      return NextResponse.json(
        { error: 'Contract text must be at least 20 characters.' },
        { status: 400 }
      )
    }

    // ── Mock mode (development / no GPU) ─────────────────────────────────────
    if (USE_MOCK) {
      // Simulate processing delay
      await new Promise(r => setTimeout(r, 1800))

      // Scale the mock score based on text content keywords
      const riskKeywords = [
        'uncapped', 'unlimited liability', 'no cap', 'liquidated damages',
        'intellectual property', 'ip ownership', 'assigned to vendor',
        'auto-renews', 'non-compete', 'change of control',
      ]
      const textLower = text.toLowerCase()
      const hits = riskKeywords.filter(k => textLower.includes(k)).length
      const scaledScore = Math.min(100, 20 + hits * 12)

      const triage =
        scaledScore < 30 ? 'AUTO-CLEAR'
        : scaledScore < 65 ? 'FLAG FOR REVIEW'
        : 'URGENT REVIEW'

      // Return proportional subset of mock clauses
      const clauseCount = Math.max(1, Math.round((scaledScore / 100) * MOCK_RESULT.clauses.length))
      return NextResponse.json({
        ...MOCK_RESULT,
        score: scaledScore,
        triage,
        word_count: text.split(/\s+/).length,
        n_clauses_detected: clauseCount,
        clauses: MOCK_RESULT.clauses.slice(0, clauseCount),
      })
    }

    // ── Real backend (Python model) ───────────────────────────────────────────
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(120_000),  // 2 min timeout
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (err: any) {
    console.error('Analysis error:', err)
    return NextResponse.json(
      { error: err.message ?? 'Analysis failed. Is the backend running?' },
      { status: 500 }
    )
  }
}
