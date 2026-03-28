'use client'

import { useEffect, useRef } from 'react'

interface Props {
  score: number          // 0–100
  size?: number          // px
  animate?: boolean
}

export default function RiskGauge({ score, size = 200, animate = true }: Props) {
  const ringRef = useRef<SVGCircleElement>(null)
  const r       = 42
  const circum  = 2 * Math.PI * r           // ≈ 263.9
  const filled  = (score / 100) * circum
  const offset  = circum - filled

  // Color ramp: green → amber → red
  const getColor = (s: number) => {
    if (s < 30) return '#2ECC71'
    if (s < 65) return '#E8943A'
    return '#C0392B'
  }
  const color = getColor(score)

  // Label
  const label =
    score < 30  ? 'LOW RISK'
    : score < 65 ? 'REVIEW'
    : 'URGENT'

  useEffect(() => {
    if (!ringRef.current || !animate) return
    // Start at zero, animate to target
    ringRef.current.style.strokeDashoffset = String(circum)
    const id = setTimeout(() => {
      if (ringRef.current) {
        ringRef.current.style.strokeDashoffset = String(offset)
      }
    }, 120)
    return () => clearTimeout(id)
  }, [score, offset, circum, animate])

  const cx = size / 2
  const cy = size / 2
  const radiusPx = (r / 50) * (size / 2)     // scale r to px

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 100 100">
        {/* Tick marks */}
        {Array.from({ length: 20 }).map((_, i) => {
          const angle = (i / 20) * 360 - 90
          const rad   = (angle * Math.PI) / 180
          const inner = 44, outer = 46.5
          const x1 = 50 + inner * Math.cos(rad)
          const y1 = 50 + inner * Math.sin(rad)
          const x2 = 50 + outer * Math.cos(rad)
          const y2 = 50 + outer * Math.sin(rad)
          return (
            <line
              key={i}
              x1={x1} y1={y1} x2={x2} y2={y2}
              stroke="rgba(201,147,58,0.15)"
              strokeWidth="0.5"
            />
          )
        })}

        {/* Track ring */}
        <circle
          cx="50" cy="50" r={r}
          fill="none"
          stroke="rgba(42, 64, 96, 0.8)"
          strokeWidth="7"
          strokeLinecap="round"
        />

        {/* Glow effect */}
        <circle
          cx="50" cy="50" r={r}
          fill="none"
          stroke={color}
          strokeWidth="9"
          strokeLinecap="round"
          strokeDasharray={circum}
          strokeDashoffset={offset}
          style={{
            filter: `drop-shadow(0 0 6px ${color}66)`,
            opacity: 0.3,
            transition: animate ? 'stroke-dashoffset 1.4s cubic-bezier(0.34,1.56,0.64,1)' : 'none',
            transform: 'rotate(-90deg)',
            transformOrigin: '50% 50%',
          }}
        />

        {/* Main ring */}
        <circle
          ref={ringRef}
          cx="50" cy="50" r={r}
          fill="none"
          stroke={color}
          strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray={circum}
          strokeDashoffset={animate ? circum : offset}
          style={{
            transition: animate ? 'stroke-dashoffset 1.4s cubic-bezier(0.34,1.56,0.64,1)' : 'none',
            transform: 'rotate(-90deg)',
            transformOrigin: '50% 50%',
          }}
        />

        {/* Center score */}
        <text
          x="50" y="44"
          textAnchor="middle"
          fontSize="22"
          fontWeight="700"
          fontFamily="'Playfair Display', Georgia, serif"
          fill={color}
        >
          {score}
        </text>
        <text
          x="50" y="53"
          textAnchor="middle"
          fontSize="5.5"
          fill="rgba(245,237,214,0.4)"
          fontFamily="'IBM Plex Mono', monospace"
          letterSpacing="0.08em"
        >
          / 100
        </text>
        <text
          x="50" y="62"
          textAnchor="middle"
          fontSize="5"
          fill={color}
          fontFamily="'IBM Plex Mono', monospace"
          letterSpacing="0.12em"
          fontWeight="600"
        >
          {label}
        </text>
      </svg>
    </div>
  )
}
