'use client'

import { useEffect, useState } from 'react'
import { getWatchlist, removeFromWatchlist, calculateRatio } from '@/lib/api'
import type { WatchlistItem } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import SignalBadge from './SignalBadge'

function PctArrow({ value }: { value: number | null | undefined }) {
  if (value == null) return <span style={{ color: '#787b86' }}>—</span>
  const up = value >= 0
  return (
    <span style={{ color: up ? '#26a69a' : '#ef5350', fontSize: 12 }}>
      {up ? '▲' : '▼'} {Math.abs(value).toFixed(2)}%
    </span>
  )
}

export default function Watchlist() {
  const {
    watchlist, setWatchlist,
    activeItem, setActiveItem,
    setChartData, setChartLoading, setChartError,
    timeframe,
  } = useAppStore()

  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      setLoading(true)
      const items = await getWatchlist()
      setWatchlist(items)
    } catch (e) {
      console.error('Watchlist load failed', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // Refresh every 5 min
    const t = setInterval(load, 5 * 60 * 1000)
    return () => clearInterval(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSelect = async (item: WatchlistItem) => {
    setActiveItem(item)
    setChartLoading(true)
    setChartError(null)
    try {
      const data = await calculateRatio(item.asset_a, item.asset_b, timeframe)
      setChartData(data)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to load chart'
      setChartError(msg)
    } finally {
      setChartLoading(false)
    }
  }

  const handleRemove = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation()
    if (!confirm('Remove from watchlist?')) return
    try {
      await removeFromWatchlist(id)
      await load()
    } catch {
      alert('Failed to remove item')
    }
  }

  if (loading) return (
    <div style={{ padding: 16, color: '#787b86', fontSize: 13 }}>Loading watchlist…</div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid #2a2e39',
        fontSize: 13,
        fontWeight: 600,
        color: '#d1d4dc',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span>Watchlist</span>
        <button
          className="btn-secondary"
          style={{ fontSize: 11, padding: '3px 8px' }}
          onClick={load}
        >↻</button>
      </div>

      <div style={{ overflowY: 'auto', flex: 1 }}>
        {watchlist.length === 0 && (
          <div style={{ padding: 16, color: '#787b86', fontSize: 13 }}>
            No ratios saved yet. Use the builder →
          </div>
        )}
        {watchlist.map((item) => {
          const isActive = activeItem?.id === item.id
          return (
            <div
              key={item.id}
              onClick={() => handleSelect(item)}
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid #2a2e39',
                cursor: 'pointer',
                background: isActive ? '#1e222d' : 'transparent',
                transition: 'background 0.1s',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = '#16181f'
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = 'transparent'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span style={{ fontSize: 13, fontWeight: 500, color: '#d1d4dc' }}>
                  {item.name}
                </span>
                <button
                  onClick={(e) => handleRemove(e, item.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#787b86',
                    fontSize: 16,
                    padding: '0 2px',
                    lineHeight: 1,
                  }}
                  title="Remove"
                >×</button>
              </div>

              <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                {item.current_value != null && (
                  <span style={{ fontSize: 13, fontWeight: 600, color: '#d1d4dc' }}>
                    {item.current_value.toFixed(4)}
                  </span>
                )}
                {item.signal && (
                  <SignalBadge signal={item.signal} zscore={item.current_zscore} size="sm" />
                )}
                <PctArrow value={item.pct_change_1w} />
              </div>

              <div style={{ marginTop: 4, fontSize: 11, color: '#787b86' }}>
                {item.asset_a.label || item.asset_a.key} / {item.asset_b.label || item.asset_b.key}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
