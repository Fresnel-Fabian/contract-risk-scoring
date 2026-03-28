'use client'

import { useState } from 'react'
import { ChevronDown, AlertTriangle, Shield, Info } from 'lucide-react'
import { DetectedClause, RISK_COLORS, RISK_LABELS } from '@/lib/types'
import clsx from 'clsx'

interface Props {
  clause: DetectedClause
  index:  number
}

export default function ClauseCard({ clause, index }: Props) {
  const [open, setOpen] = useState(index < 3)

  const color = RISK_COLORS[clause.risk_weight] ?? '#8CA0BB'
  const label = RISK_LABELS[clause.risk_weight] ?? 'Low'
  const pct   = Math.round(clause.confidence * 100)
  const isHigh = clause.risk_weight >= 7

  const Icon = clause.risk_weight >= 8 ? AlertTriangle
             : clause.risk_weight >= 5 ? Shield
             : Info

  return (
    <div
      className={clsx(
        'glass glass-hover rounded-lg overflow-hidden',
        'border transition-all duration-300',
        isHigh ? 'border-orange-900/30' : 'border-edge/50'
      )}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {/* Header */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3.5 text-left"
      >
        {/* Icon */}
        <div
          className="flex-shrink-0 w-7 h-7 rounded-md flex items-center justify-center"
          style={{ background: `${color}18`, border: `1px solid ${color}40` }}
        >
          <Icon size={13} style={{ color }} />
        </div>

        {/* Clause name */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className="font-mono text-sm font-medium truncate"
              style={{ color: clause.risk_weight >= 7 ? '#F5EDD6' : '#B8CCDF' }}
            >
              {clause.clause}
            </span>
            {isHigh && (
              <span
                className="flex-shrink-0 text-[9px] font-mono font-semibold tracking-widest uppercase px-1.5 py-0.5 rounded"
                style={{ background: `${color}22`, color, border: `1px solid ${color}44` }}
              >
                {label}
              </span>
            )}
          </div>

          {/* Probability bar */}
          <div className="flex items-center gap-2 mt-1.5">
            <div className="prob-bar flex-1" style={{ maxWidth: 120 }}>
              <div
                className="prob-fill"
                style={{ width: `${pct}%`, background: color }}
              />
            </div>
            <span className="font-mono text-[10px] text-slate/60">{pct}%</span>
          </div>
        </div>

        {/* Weight badge */}
        <div className="flex-shrink-0 flex items-center gap-2">
          <div className="text-right">
            <div
              className="font-mono text-xs font-semibold"
              style={{ color }}
            >
              {clause.risk_weight}/10
            </div>
            <div className="text-[9px] font-mono text-slate/50 uppercase tracking-wider">
              weight
            </div>
          </div>
          <ChevronDown
            size={14}
            className="text-slate/40 transition-transform duration-200"
            style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }}
          />
        </div>
      </button>

      {/* Extracted text */}
      {open && (
        <div
          className="px-4 pb-4 pt-1"
          style={{ borderTop: `1px solid ${color}18` }}
        >
          <div className="text-xs font-mono text-slate/50 uppercase tracking-widest mb-2">
            Extracted clause text
          </div>
          <blockquote
            className="font-body text-sm leading-relaxed italic"
            style={{
              color: '#D4C4A8',
              borderLeft: `2px solid ${color}60`,
              paddingLeft: '12px',
            }}
          >
            "{clause.text}"
          </blockquote>
        </div>
      )}
    </div>
  )
}
