'use client'

import { useState, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import {
  Scale, Upload, FileText, Zap,
  Shield, AlertTriangle, ChevronRight, Loader2,
} from 'lucide-react'
import type { ScoreResult } from '@/lib/types'

const SAMPLES = {
  high: {
    label: 'High-Risk SaaS',
    tag: 'URGENT',
    text: `SOFTWARE AS A SERVICE AGREEMENT

This Agreement is entered into between TechVendor Inc. ("Vendor") and Customer Corp ("Customer").

1. LICENSE. Vendor grants Customer a non-exclusive, non-transferable license. All intellectual property created under this Agreement shall be assigned to Vendor, including any derivative works.

2. LIABILITY. There shall be no cap on liability under any circumstances — Vendor's liability shall not be limited or capped. Customer waives all limitation of liability defenses.

3. TERM. This Agreement auto-renews annually unless terminated with 90 days prior written notice. 

4. GOVERNING LAW. This Agreement shall be governed by the laws of the State of Delaware.

5. NON-COMPETE. Customer agrees not to engage with competing vendors for 24 months following termination.

6. DAMAGES. Customer shall pay $500,000 as liquidated damages for any breach of exclusivity.

7. CHANGE OF CONTROL. Any acquisition of Customer requires prior written consent from Vendor.

8. ESCROW. Vendor shall deposit source code into an escrow account.`,
  },
  mid: {
    label: 'Mid-Risk MSA',
    tag: 'REVIEW',
    text: `MASTER SERVICES AGREEMENT

This Master Services Agreement is entered into between Services LLC ("Vendor") and Client Corp ("Client").

1. SERVICES. Vendor will provide software development services as described in statements of work.

2. IP. Client retains all intellectual property rights to deliverables created under this Agreement.

3. LIABILITY. Vendor liability shall be limited to fees paid in the prior 12 months.

4. GOVERNING LAW. Governing law is New York. Either party may terminate for convenience with 60 days notice.

5. NON-SOLICIT. Vendor agrees not to solicit Client employees during the term and for 12 months after termination.

6. REVENUE SHARING. Revenue sharing of 15% applies to any sublicensing by Client.

7. RENEWAL. Renewal is automatic for successive one-year terms unless terminated.`,
  },
  low: {
    label: 'Low-Risk NDA',
    tag: 'CLEAR',
    text: `NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of January 1, 2026 between Party A ("Disclosing Party") and Party B ("Receiving Party").

1. CONFIDENTIALITY. The Receiving Party agrees to keep all Confidential Information strictly confidential.

2. PURPOSE. Confidential Information may only be used for evaluating a potential business relationship.

3. GOVERNING LAW. This Agreement is governed by the laws of the State of Delaware.

4. TERM. The term of this Agreement is two years from the effective date.

5. TERMINATION. Either party may terminate with 30 days written notice.

6. ENTIRE AGREEMENT. This Agreement constitutes the entire understanding between the parties regarding confidentiality.`,
  },
}

export default function HomePage() {
  const router  = useRouter()
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const [dragging, setDragging] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const analyze = useCallback(async (contractText: string) => {
    if (!contractText.trim() || contractText.trim().length < 20) {
      setError('Please paste contract text (at least 20 characters).')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: contractText }),
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        throw new Error(d.error ?? `Error ${res.status}`)
      }
      const data: ScoreResult = await res.json()
      sessionStorage.setItem('lex_result', JSON.stringify(data))
      sessionStorage.setItem('lex_text',   contractText)
      router.push('/analyze')
    } catch (e: any) {
      setError(e.message ?? 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }, [router])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = ev => setText(ev.target?.result as string ?? '')
    reader.readAsText(file)
  }, [])

  const TagColors: Record<string, string> = {
    URGENT: '#C0392B',
    REVIEW: '#E8943A',
    CLEAR:  '#2ECC71',
  }

  return (
    <main className="min-h-screen flex flex-col">
      {/* ── Background mesh ─────────────────────────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none">
        <div
          className="absolute top-0 left-1/4 w-[600px] h-[600px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(201,147,58,0.06) 0%, transparent 70%)',
            filter: 'blur(40px)',
          }}
        />
        <div
          className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(30,107,64,0.04) 0%, transparent 70%)',
            filter: 'blur(40px)',
          }}
        />
      </div>

      {/* ── Header ───────────────────────────────────────────────────────── */}
      <header className="relative z-10 flex items-center justify-between px-8 py-6">
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-md flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, #C9933A, #B8832A)',
              boxShadow: '0 2px 12px rgba(201,147,58,0.3)',
            }}
          >
            <Scale size={15} className="text-void" strokeWidth={2.5} />
          </div>
          <span className="font-display text-lg font-bold tracking-tight text-cream">Lex</span>
          <span className="font-mono text-xs text-slate/50 tracking-widest uppercase mt-0.5">
            · Contract Risk Engine
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="dot-pulse w-1.5 h-1.5 rounded-full bg-amber" />
          <span className="font-mono text-[10px] text-slate/50 tracking-widest uppercase">
            CUAD · RoBERTa · 41 clause types
          </span>
        </div>
      </header>

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="relative z-10 px-8 pt-12 pb-8 max-w-3xl mx-auto w-full">
        <div className="fade-up">
          <p className="font-mono text-[11px] text-amber/70 tracking-[0.2em] uppercase mb-4">
            Fresnel Fabian · MPS Applied Machine Intelligence · Northeastern Roux
          </p>
          <h1 className="font-display text-5xl font-bold leading-[1.1] mb-5">
            <span className="text-cream">Know what you're</span>
            <br />
            <span className="text-amber-gradient">signing.</span>
          </h1>
          <p className="font-body text-lg text-slate/70 max-w-xl leading-relaxed">
            Paste any contract. The model reads all 41 clause types in seconds —
            extracting the exact text of each risk, weighted by legal impact.
          </p>
        </div>
      </section>

      {/* ── Stats strip ──────────────────────────────────────────────────── */}
      <section className="relative z-10 px-8 pb-8 max-w-3xl mx-auto w-full">
        <div className="fade-up delay-200 flex items-center gap-6">
          {[
            { val: '510', label: 'Training contracts' },
            { val: '41',  label: 'Clause types' },
            { val: '4',   label: 'Epochs trained' },
            { val: 'QA',  label: 'Extractive model' },
          ].map(s => (
            <div key={s.label} className="flex items-baseline gap-1.5">
              <span className="font-mono text-xl font-semibold text-amber">{s.val}</span>
              <span className="font-mono text-[10px] text-slate/50 uppercase tracking-wider">{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── Main input card ───────────────────────────────────────────────── */}
      <section className="relative z-10 px-8 pb-12 max-w-3xl mx-auto w-full flex-1">
        <div className="fade-up delay-300 glass rounded-xl overflow-hidden">

          {/* Sample contract pills */}
          <div className="px-5 pt-5 pb-4 flex items-center gap-3 flex-wrap">
            <span className="font-mono text-[10px] text-slate/40 uppercase tracking-widest mr-1">
              Try:
            </span>
            {Object.entries(SAMPLES).map(([key, s]) => (
              <button
                key={key}
                onClick={() => setText(s.text)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs
                           transition-all duration-200 hover:scale-105"
                style={{
                  background: `${TagColors[s.tag]}14`,
                  border: `1px solid ${TagColors[s.tag]}35`,
                  color: TagColors[s.tag],
                }}
              >
                <span>{s.label}</span>
              </button>
            ))}
          </div>

          <div className="divider-amber mx-5" />

          {/* Textarea */}
          <div
            className={`drop-zone mx-5 my-4 rounded-lg overflow-hidden relative ${dragging ? 'dragging' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >
            {loading && <div className="scan-line" />}
            <textarea
              ref={textareaRef}
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Paste contract text here, or drag + drop a .txt file…"
              className="w-full h-64 bg-transparent resize-none outline-none
                         font-body text-sm leading-relaxed p-4
                         placeholder:text-slate/25 text-fog/90"
              disabled={loading}
            />
          </div>

          {/* Footer row */}
          <div className="px-5 pb-5 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              {text.trim() && (
                <span className="font-mono text-[10px] text-slate/40 uppercase tracking-wider">
                  {text.trim().split(/\s+/).length.toLocaleString()} words
                </span>
              )}
              {error && (
                <span className="font-mono text-[11px] text-red-400">{error}</span>
              )}
              {!text && (
                <span className="font-mono text-[10px] text-slate/30 uppercase tracking-wider">
                  or drag a .txt file
                </span>
              )}
            </div>

            <button
              onClick={() => analyze(text)}
              disabled={loading || !text.trim()}
              className="btn-amber flex items-center gap-2 px-6 py-3 rounded-lg
                         disabled:opacity-30 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  <span>Analyzing…</span>
                </>
              ) : (
                <>
                  <Zap size={14} />
                  <span>Analyze Contract</span>
                  <ChevronRight size={12} />
                </>
              )}
            </button>
          </div>
        </div>

        {/* How it works */}
        <div className="fade-up delay-500 mt-8 grid grid-cols-3 gap-4">
          {[
            {
              icon: FileText,
              title: 'Extractive QA',
              body: 'Asks 41 questions about your contract. Returns the exact text of each clause — not a classification.',
            },
            {
              icon: Shield,
              title: 'Impact weighted',
              body: 'Uncapped Liability = 10. IP Assignment = 9. Audit Rights = 6. Each clause weighted by legal consequence.',
            },
            {
              icon: AlertTriangle,
              title: 'Three-tier triage',
              body: 'AUTO-CLEAR, FLAG FOR REVIEW, or URGENT REVIEW — calibrated for a mid-market legal ops team.',
            },
          ].map(({ icon: Icon, title, body }) => (
            <div
              key={title}
              className="glass rounded-lg p-4 border border-edge/40"
            >
              <div
                className="w-7 h-7 rounded-md flex items-center justify-center mb-3"
                style={{ background: 'rgba(201,147,58,0.1)', border: '1px solid rgba(201,147,58,0.2)' }}
              >
                <Icon size={13} className="text-amber" />
              </div>
              <div className="font-mono text-[11px] font-semibold text-cream/80 uppercase tracking-wider mb-1.5">
                {title}
              </div>
              <div className="font-body text-xs text-slate/60 leading-relaxed">{body}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
