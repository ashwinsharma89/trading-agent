'use client'

import dynamic from 'next/dynamic'
import { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'
import { getZerodhaAuthStatus } from '@/lib/api'
import SignalBadge from '@/components/SignalBadge'
import type { Timeframe } from '@/lib/api'

const RatioChart    = dynamic(() => import('@/components/RatioChart'),    { ssr: false })
const Watchlist     = dynamic(() => import('@/components/Watchlist'),     { ssr: false })
const RatioBuilder  = dynamic(() => import('@/components/RatioBuilder'),  { ssr: false })
const SectorHeatmap = dynamic(() => import('@/components/SectorHeatmap'), { ssr: false })

const TIMEFRAMES: Timeframe[] = ['1M', '3M', '6M', '1Y', '3Y', '5Y']
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function AuthBanner({ source, token }: { source: string; token: boolean }) {
  if (token) return null
  return (
    <div style={{
      background: '#7c2020',
      color: '#ffcdd2',
      padding: '8px 16px',
      fontSize: 13,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 12,
    }}>
      <span>
        ⚠ Zerodha access token missing or expired — Indian market data unavailable.
      </span>
      <a
        href={`${API_URL}/auth/zerodha/login`}
        style={{
          background: '#ef5350',
          color: '#fff',
          padding: '4px 12px',
          borderRadius: 4,
          fontSize: 12,
          fontWeight: 600,
          textDecoration: 'none',
        }}
      >
        Re-authenticate with Zerodha →
      </a>
    </div>
  )
}

function FallbackBanner({ show }: { show: boolean }) {
  if (!show) return null
  return (
    <div style={{
      background: '#1a3a4a',
      color: '#80cbc4',
      padding: '6px 16px',
      fontSize: 12,
    }}>
      ℹ Using fallback data source (Upstox). Some data may differ slightly.
    </div>
  )
}

export default function DashboardPage() {
  const {
    chartData, chartLoading, chartError,
    showZscore, setShowZscore,
    showRsi, setShowRsi,
    timeframe, setTimeframe,
    zerodhaAuthRequired, setZerodhaAuthRequired,
    usingFallback,
    activeItem,
  } = useAppStore()

  const [activeTab, setActiveTab] = useState<'chart' | 'heatmap'>('chart')

  useEffect(() => {
    getZerodhaAuthStatus()
      .then(({ token_configured }) => {
        setZerodhaAuthRequired(!token_configured)
      })
      .catch(() => {})
  }, [setZerodhaAuthRequired])

  const chartTitle = activeItem
    ? activeItem.name
    : chartData
      ? `${chartData.asset_a_label} / ${chartData.asset_b_label}`
      : 'Select a ratio'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      {/* Top bar */}
      <header style={{
        background: '#131722',
        borderBottom: '1px solid #2a2e39',
        padding: '10px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        flexShrink: 0,
      }}>
        <span style={{ fontSize: 16, fontWeight: 700, color: '#d1d4dc', letterSpacing: '0.5px' }}>
          📊 Ratio Chart
        </span>
        <span style={{ color: '#2a2e39', fontSize: 18 }}>|</span>
        <span style={{ color: '#787b86', fontSize: 12 }}>Indian Market · Real-time (15-min delayed)</span>
      </header>

      {/* Auth banners */}
      <AuthBanner source="zerodha" token={!zerodhaAuthRequired} />
      <FallbackBanner show={usingFallback} />

      {/* Main layout */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* Left: Watchlist */}
        <div style={{
          width: 260,
          flexShrink: 0,
          borderRight: '1px solid #2a2e39',
          background: '#131722',
          overflowY: 'auto',
        }}>
          <Watchlist />
        </div>

        {/* Center: Charts */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

          {/* Chart toolbar */}
          <div style={{
            background: '#131722',
            borderBottom: '1px solid #2a2e39',
            padding: '8px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            flexShrink: 0,
            flexWrap: 'wrap',
          }}>
            {/* Tabs */}
            {(['chart', 'heatmap'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  background: activeTab === tab ? '#2962ff' : 'transparent',
                  color: activeTab === tab ? '#fff' : '#787b86',
                  border: '1px solid ' + (activeTab === tab ? '#2962ff' : '#2a2e39'),
                  padding: '4px 12px',
                  borderRadius: 4,
                  fontSize: 12,
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                {tab === 'chart' ? 'Ratio Chart' : 'Sector Heatmap'}
              </button>
            ))}

            {activeTab === 'chart' && (
              <>
                <span style={{ color: '#2a2e39' }}>|</span>

                {/* Timeframe */}
                {TIMEFRAMES.map((tf) => (
                  <button
                    key={tf}
                    onClick={() => setTimeframe(tf)}
                    style={{
                      background: timeframe === tf ? '#1e222d' : 'transparent',
                      color: timeframe === tf ? '#d1d4dc' : '#787b86',
                      border: 'none',
                      padding: '3px 8px',
                      borderRadius: 3,
                      fontSize: 12,
                      cursor: 'pointer',
                    }}
                  >
                    {tf}
                  </button>
                ))}

                <span style={{ color: '#2a2e39' }}>|</span>

                {/* Panel toggles */}
                {[
                  { label: 'Z-Score', val: showZscore, set: setShowZscore },
                  { label: 'RSI',     val: showRsi,    set: setShowRsi },
                ].map(({ label, val, set }) => (
                  <button
                    key={label}
                    onClick={() => set(!val)}
                    style={{
                      background: val ? '#1e222d' : 'transparent',
                      color: val ? '#d1d4dc' : '#2a2e39',
                      border: '1px solid ' + (val ? '#2a2e39' : '#1e222d'),
                      padding: '3px 8px',
                      borderRadius: 3,
                      fontSize: 11,
                      cursor: 'pointer',
                    }}
                  >
                    {label}
                  </button>
                ))}

                {chartData && (
                  <>
                    <span style={{ color: '#2a2e39' }}>|</span>
                    <SignalBadge signal={chartData.signal} zscore={chartData.current_zscore} />
                    <span style={{ fontSize: 12, color: '#787b86' }}>
                      {chartTitle}
                    </span>
                    {chartData.note && (
                      <span style={{ fontSize: 11, color: '#787b86', fontStyle: 'italic' }}>
                        ({chartData.note})
                      </span>
                    )}
                  </>
                )}
              </>
            )}
          </div>

          {/* Chart / heatmap area */}
          <div style={{ flex: 1, overflowY: 'auto', padding: 16, background: '#0d1117' }}>
            {activeTab === 'heatmap' ? (
              <div className="card">
                <SectorHeatmap />
              </div>
            ) : (
              <>
                {chartLoading && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: 300,
                    color: '#787b86',
                    fontSize: 14,
                  }}>
                    Loading chart data…
                  </div>
                )}
                {chartError && (
                  <div style={{
                    background: '#2c1010',
                    border: '1px solid #7c2020',
                    borderRadius: 8,
                    padding: 16,
                    color: '#ef5350',
                    fontSize: 13,
                  }}>
                    ⚠ {chartError}
                  </div>
                )}
                {!chartLoading && !chartError && chartData && (
                  <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <RatioChart
                      data={chartData}
                      showZscore={showZscore}
                      showRsi={showRsi}
                      assetALabel={chartData.asset_a_label}
                      assetBLabel={chartData.asset_b_label}
                    />
                  </div>
                )}
                {!chartLoading && !chartError && !chartData && (
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: 300,
                    color: '#787b86',
                    fontSize: 14,
                    gap: 8,
                  }}>
                    <div style={{ fontSize: 40 }}>📈</div>
                    <div>Select a ratio from the watchlist or build a new one →</div>
                  </div>
                )}

                {/* Metrics strip */}
                {chartData && !chartLoading && (
                  <div style={{
                    display: 'flex',
                    gap: 16,
                    marginTop: 16,
                    flexWrap: 'wrap',
                  }}>
                    {[
                      { label: 'Current Value', val: chartData.current_value.toFixed(4) },
                      { label: 'Z-Score',       val: chartData.current_zscore.toFixed(2) },
                      { label: '1W Change',     val: chartData.pct_change_1w != null ? `${chartData.pct_change_1w > 0 ? '+' : ''}${chartData.pct_change_1w.toFixed(2)}%` : '—' },
                      { label: '1M Change',     val: chartData.pct_change_1m != null ? `${chartData.pct_change_1m > 0 ? '+' : ''}${chartData.pct_change_1m.toFixed(2)}%` : '—' },
                      { label: '3M Change',     val: chartData.pct_change_3m != null ? `${chartData.pct_change_3m > 0 ? '+' : ''}${chartData.pct_change_3m.toFixed(2)}%` : '—' },
                    ].map(({ label, val }) => (
                      <div key={label} className="card" style={{ padding: '10px 16px', minWidth: 120 }}>
                        <div style={{ fontSize: 11, color: '#787b86', marginBottom: 4 }}>{label}</div>
                        <div style={{ fontSize: 15, fontWeight: 600, color: '#d1d4dc', fontFamily: 'monospace' }}>{val}</div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Right: Builder */}
        <div style={{
          width: 320,
          flexShrink: 0,
          borderLeft: '1px solid #2a2e39',
          background: '#131722',
          overflowY: 'auto',
          padding: 16,
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
        }}>
          <RatioBuilder />
        </div>

      </div>
    </div>
  )
}
