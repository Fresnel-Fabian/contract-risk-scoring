'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Scale, ArrowLeft, Download, Copy, Check,
  AlertTriangle, Clock, CheckCircle2,
  BarChart3, FileSearch, Layers,
} from 'lucide-react'
import RiskGauge    from '@/components/RiskGauge'
import ClauseCard   from '@/components/ClauseCard'
import { ScoreResult, RISK_COLORS } from '@/lib/types'
import clsx from 'clsx'

export default function AnalyzePage() {
  const router = useRouter()
  const [result,   setResult]   = useState<ScoreResult | null>(null)
  const [text,     setText]     = useState('')
  const [copied,   setCopied]   = useState(false)
  const [activeTab, setActiveTab] = useState<'clauses' | 'breakdown'>('clauses')

  useEffect(() => {
    const r = sessionStorage.getItem('lex_result')
    const t = sessionStorage.getItem('lex_text')
    if (!r) { router.replace('/'); return }
    setResult(JSON.parse(r))
    setText(t ?? '')
  }, [router])

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-3 font-mono text-sm text-slate/50">
          <div className="w-4 h-4 border-2 border-amber border-t-transparent rounded-full animate-spin" />
          Loading…
        </div>
      </div>
    )
  }

  const triageConfig = {
    'URGENT REVIEW': {
      color: '#C0392B', bg: 'rgba(192,57,43,0.12)',
      border: 'rgba(192,57,43,0.4)',
      icon: AlertTriangle, label: 'URGENT REVIEW',
      desc: 'High-risk clauses detected. Requires immediate legal review before signing.',
    },
    'FLAG FOR REVIEW': {
      color: '#E8943A', bg: 'rgba(232,148,58,0.12)',
      border: 'rgba(232,148,58,0.4)',
      icon: Clock, label: 'FLAG FOR REVIEW',
      desc: 'Moderate risk detected. Schedule legal review within standard SLA.',
    },
    'AUTO-CLEAR': {
      color: '#2ECC71', bg: 'rgba(46,204,113,0.12)',
      border: 'rgba(46,204,113,0.4)',
      icon: CheckCircle2, label: 'AUTO-CLEAR',
      desc: 'Low-risk contract. No immediate legal review required.',
    },
  }

  const tc = triageConfig[result.triage]
  const TriageIcon = tc.icon

  const handleCopy = () => {
    const lines = [
      `Contract Risk Score: ${result.score}/100`,
      `Triage: ${result.triage}`,
      `Detected clauses: ${result.n_clauses_detected}`,
      '',
      ...result.clauses.map(c =>
        `[${c.risk_weight}/10] ${c.clause}: "${c.text.slice(0, 100)}…"`
      ),
    ]
    navigator.clipboard.writeText(lines.join('\n'))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // For breakdown chart: group clauses by risk tier
  const tierData = [
    { label: 'Critical (8–10)', min: 8,  max: 10, color: '#C0392B' },
    { label: 'High (6–7)',      min: 6,  max: 7,  color: '#E8943A' },
    { label: 'Moderate (4–5)', min: 4,  max: 5,  color: '#C9933A' },
    { label: 'Low (1–3)',      min: 1,  max: 3,  color: '#5D7A9A' },
  ].map(tier => ({
    ...tier,
    count: result.clauses.filter(c => c.risk_weight >= tier.min && c.risk_weight <= tier.max).length,
  }))

  const maxTierCount = Math.max(...tierData.map(t => t.count), 1)

  return (
    <main className="min-h-screen flex flex-col">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div
          className="absolute top-0 right-1/4 w-[500px] h-[500px] rounded-full"
          style={{
            background: `radial-gradient(circle, ${tc.color}08 0%, transparent 70%)`,
            filter: 'blur(60px)',
          }}
        />
      </div>

      {/* ── Header ───────────────────────────────────────────────────────── */}
      <header className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-edge/30">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 font-mono text-xs text-slate/50
                       hover:text-amber transition-colors duration-200"
          >
            <ArrowLeft size={13} />
            <span className="uppercase tracking-widest">New analysis</span>
          </button>
          <div className="w-px h-4 bg-edge" />
          <div className="flex items-center gap-2">
            <Scale size={13} className="text-amber" />
            <span className="font-display text-base font-bold text-cream">Lex</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-[10px]
                       text-slate/50 hover:text-amber border border-edge/40 hover:border-amber/30
                       transition-all duration-200 uppercase tracking-widest"
          >
            {copied ? <Check size={11} /> : <Copy size={11} />}
            {copied ? 'Copied' : 'Export'}
          </button>
        </div>
      </header>

      <div className="relative z-10 flex-1 px-8 py-8 max-w-5xl mx-auto w-full">
        <div className="grid grid-cols-[280px_1fr] gap-6">

          {/* ── Left sidebar ─────────────────────────────────────────────── */}
          <aside className="space-y-4">

            {/* Risk score gauge */}
            <div className="fade-up glass rounded-xl p-6 flex flex-col items-center">
              <RiskGauge score={result.score} size={160} />
              <div
                className="mt-4 w-full rounded-lg px-4 py-3 text-center"
                style={{ background: tc.bg, border: `1px solid ${tc.border}` }}
              >
                <div className="flex items-center justify-center gap-1.5 mb-1">
                  <TriageIcon size={12} style={{ color: tc.color }} />
                  <span
                    className="font-mono text-[11px] font-bold tracking-[0.12em] uppercase"
                    style={{ color: tc.color }}
                  >
                    {tc.label}
                  </span>
                </div>
                <p className="font-body text-[11px] text-slate/60 leading-snug">
                  {tc.desc}
                </p>
              </div>
            </div>

            {/* Metadata */}
            <div className="fade-up delay-100 glass rounded-xl p-4 space-y-3">
              {[
                { icon: FileSearch, label: 'Words scanned',  val: result.word_count.toLocaleString() },
                { icon: Layers,     label: 'Clauses found',  val: `${result.n_clauses_detected} / 41` },
                { icon: BarChart3,  label: 'Confidence threshold', val: `${Math.round(result.threshold * 100)}%` },
              ].map(({ icon: Icon, label, val }) => (
                <div key={label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon size={12} className="text-slate/40" />
                    <span className="font-mono text-[10px] text-slate/50 uppercase tracking-wider">
                      {label}
                    </span>
                  </div>
                  <span className="font-mono text-xs font-semibold text-cream/70">{val}</span>
                </div>
              ))}
            </div>

            {/* Model badge */}
            <div className="fade-up delay-200">
              <div className="font-mono text-[9px] text-slate/30 uppercase tracking-widest mb-1.5 px-1">
                Model
              </div>
              <div className="glass rounded-lg px-3 py-2">
                <div className="font-mono text-[10px] text-amber/70 leading-relaxed">
                  {result.model}
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <p className="font-body text-[10px] text-slate/30 leading-relaxed px-1 italic">
              This tool flags clauses for review — it does not provide legal advice.
              Always consult a qualified attorney before signing.
            </p>
          </aside>

          {/* ── Right main panel ─────────────────────────────────────────── */}
          <div className="space-y-4">

            {/* Tab switcher */}
            <div className="fade-up flex items-center gap-1 glass rounded-lg p-1 w-fit">
              {(['clauses', 'breakdown'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={clsx(
                    'px-4 py-2 rounded-md font-mono text-[11px] uppercase tracking-widest transition-all duration-200',
                    activeTab === tab
                      ? 'bg-amber text-void font-semibold'
                      : 'text-slate/50 hover:text-cream/70'
                  )}
                >
                  {tab === 'clauses' ? `Clauses (${result.clauses.length})` : 'Risk Breakdown'}
                </button>
              ))}
            </div>

            {/* ── Clauses tab ──────────────────────────────────────────── */}
            {activeTab === 'clauses' && (
              <div className="space-y-2">
                {result.clauses.length === 0 ? (
                  <div className="fade-up glass rounded-xl p-12 text-center">
                    <CheckCircle2 size={32} className="text-green-500/40 mx-auto mb-3" />
                    <div className="font-mono text-sm text-slate/50">
                      No significant clauses detected above threshold.
                    </div>
                  </div>
                ) : (
                  result.clauses.map((c, i) => (
                    <div key={c.clause} className="fade-up" style={{ animationDelay: `${i * 50}ms` }}>
                      <ClauseCard clause={c} index={i} />
                    </div>
                  ))
                )}
              </div>
            )}

            {/* ── Breakdown tab ─────────────────────────────────────────── */}
            {activeTab === 'breakdown' && (
              <div className="space-y-3">

                {/* Tier chart */}
                <div className="fade-up glass rounded-xl p-6">
                  <div className="font-mono text-[10px] text-slate/40 uppercase tracking-widest mb-5">
                    Clauses by risk tier
                  </div>
                  <div className="space-y-4">
                    {tierData.map(tier => (
                      <div key={tier.label} className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs" style={{ color: tier.color }}>
                            {tier.label}
                          </span>
                          <span className="font-mono text-xs text-slate/50">
                            {tier.count} clause{tier.count !== 1 ? 's' : ''}
                          </span>
                        </div>
                        <div className="h-5 bg-surface rounded overflow-hidden">
                          <div
                            className="h-full rounded transition-all duration-1000"
                            style={{
                              width:  `${(tier.count / maxTierCount) * 100}%`,
                              background: tier.color,
                              opacity: tier.count > 0 ? 0.85 : 0,
                              minWidth: tier.count > 0 ? 4 : 0,
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Per-clause confidence list */}
                <div className="fade-up delay-200 glass rounded-xl p-6">
                  <div className="font-mono text-[10px] text-slate/40 uppercase tracking-widest mb-4">
                    Confidence by clause
                  </div>
                  <div className="space-y-2.5">
                    {result.clauses
                      .slice()
                      .sort((a, b) => b.confidence - a.confidence)
                      .map(c => {
                        const color = RISK_COLORS[c.risk_weight] ?? '#8CA0BB'
                        const pct   = Math.round(c.confidence * 100)
                        return (
                          <div key={c.clause} className="flex items-center gap-3">
                            <span className="font-mono text-[10px] text-slate/60 w-44 truncate flex-shrink-0">
                              {c.clause}
                            </span>
                            <div className="flex-1 h-1.5 bg-surface rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full"
                                style={{ width: `${pct}%`, background: color }}
                              />
                            </div>
                            <span className="font-mono text-[10px] w-8 text-right flex-shrink-0" style={{ color }}>
                              {pct}%
                            </span>
                          </div>
                        )
                      })}
                  </div>
                </div>

                {/* Contract text preview */}
                {text && (
                  <div className="fade-up delay-300 glass rounded-xl p-6">
                    <div className="font-mono text-[10px] text-slate/40 uppercase tracking-widest mb-3">
                      Contract text preview
                    </div>
                    <div
                      className="font-body text-xs text-slate/50 leading-relaxed max-h-40 overflow-y-auto"
                      style={{ whiteSpace: 'pre-wrap' }}
                    >
                      {text.slice(0, 800)}{text.length > 800 ? '…' : ''}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
