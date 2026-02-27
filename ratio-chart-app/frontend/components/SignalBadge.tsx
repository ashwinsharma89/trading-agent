'use client'

interface Props {
  signal: string
  zscore?: number | null
  size?: 'sm' | 'md'
}

const CONFIG = {
  overbought: { label: 'Overbought', bg: '#ef5350', text: '#fff' },
  oversold:   { label: 'Oversold',   bg: '#26a69a', text: '#fff' },
  neutral:    { label: 'Neutral',    bg: '#2a2e39', text: '#787b86' },
}

export default function SignalBadge({ signal, zscore, size = 'md' }: Props) {
  const cfg = CONFIG[signal as keyof typeof CONFIG] ?? CONFIG.neutral
  const pad = size === 'sm' ? '2px 7px' : '4px 10px'
  const fs  = size === 'sm' ? '11px' : '12px'

  return (
    <span
      style={{
        background: cfg.bg,
        color: cfg.text,
        padding: pad,
        borderRadius: 4,
        fontSize: fs,
        fontWeight: 600,
        whiteSpace: 'nowrap',
      }}
    >
      {cfg.label}
      {zscore != null && (
        <span style={{ marginLeft: 6, opacity: 0.85, fontWeight: 400 }}>
          z={zscore.toFixed(2)}
        </span>
      )}
    </span>
  )
}
