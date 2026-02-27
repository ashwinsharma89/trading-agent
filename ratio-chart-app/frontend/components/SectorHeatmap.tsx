'use client'

import { useEffect, useState } from 'react'
import { getSectorHeatmap } from '@/lib/api'
import type { SectorData } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { calculateRatio } from '@/lib/api'

function zscoreToColor(z: number | null): string {
  if (z == null) return '#2a2e39'
  const clamped = Math.max(-3, Math.min(3, z))
  if (clamped >= 2)  return '#b71c1c'   // dark red – very overbought
  if (clamped >= 1)  return '#ef5350'   // red
  if (clamped >= 0.5) return '#ff7043'  // orange-red
  if (clamped >= -0.5) return '#2a2e39' // neutral
  if (clamped >= -1) return '#26a69a'   // green
  if (clamped >= -2) return '#00796b'   // dark green – oversold
  return '#004d40'                       // very dark green – very oversold
}

export default function SectorHeatmap() {
  const [sectors, setSectors] = useState<SectorData[]>([])
  const [loading, setLoading] = useState(true)
  const { setChartData, setChartLoading, setChartError, timeframe, setActiveItem } = useAppStore()

  const NIFTY50: import('@/lib/api').AssetSpec = {
    source: 'zerodha',
    key: 'NSE:NIFTY 50',
    label: 'Nifty 50',
  }

  useEffect(() => {
    getSectorHeatmap()
      .then(setSectors)
      .catch((e) => console.error('Heatmap failed', e))
      .finally(() => setLoading(false))
  }, [])

  const handleClick = async (sector: SectorData) => {
    setActiveItem(null)
    setChartLoading(true)
    setChartError(null)
    try {
      const data = await calculateRatio(
        { source: 'zerodha', key: sector.key, label: sector.name },
        NIFTY50,
        timeframe,
      )
      setChartData(data)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to load chart'
      setChartError(msg)
    } finally {
      setChartLoading(false)
    }
  }

  if (loading) return (
    <div style={{ padding: 12, color: '#787b86', fontSize: 13 }}>Loading sector heatmap…</div>
  )

  return (
    <div>
      <div style={{ fontSize: 12, fontWeight: 600, color: '#787b86', marginBottom: 10 }}>
        SECTOR vs NIFTY 50 — Z-Score Heatmap
      </div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
        gap: 6,
      }}>
        {sectors.map((s) => (
          <div
            key={s.key}
            onClick={() => handleClick(s)}
            title={`Z-score: ${s.current_zscore?.toFixed(2) ?? 'N/A'} | ${s.signal}`}
            style={{
              background: zscoreToColor(s.current_zscore),
              borderRadius: 6,
              padding: '10px 8px',
              cursor: 'pointer',
              textAlign: 'center',
              transition: 'opacity 0.15s',
              border: '1px solid rgba(255,255,255,0.05)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.8')}
            onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
          >
            <div style={{ fontSize: 12, fontWeight: 600, color: '#d1d4dc' }}>{s.name}</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)', marginTop: 3 }}>
              {s.current_zscore != null ? `z=${s.current_zscore.toFixed(2)}` : '—'}
            </div>
            {s.pct_change_1w != null && (
              <div style={{
                fontSize: 10,
                color: s.pct_change_1w >= 0 ? '#80cbc4' : '#ef9a9a',
                marginTop: 2,
              }}>
                {s.pct_change_1w >= 0 ? '+' : ''}{s.pct_change_1w.toFixed(1)}% 1W
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: 12, marginTop: 10, flexWrap: 'wrap' }}>
        {[
          { color: '#b71c1c', label: 'Very Overbought (z>2)' },
          { color: '#ef5350', label: 'Overbought (z>1)' },
          { color: '#2a2e39', label: 'Neutral' },
          { color: '#26a69a', label: 'Oversold (z<-1)' },
          { color: '#004d40', label: 'Very Oversold (z<-2)' },
        ].map((l) => (
          <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <div style={{ width: 12, height: 12, borderRadius: 2, background: l.color }} />
            <span style={{ fontSize: 10, color: '#787b86' }}>{l.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
