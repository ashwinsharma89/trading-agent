'use client'

import { useState, useEffect, useRef } from 'react'
import type { AssetSpec, InstrumentResult, Timeframe } from '@/lib/api'
import {
  searchInstruments,
  getPopularInstruments,
  calculateRatio,
  addToWatchlist,
} from '@/lib/api'
import { useAppStore } from '@/lib/store'

const SOURCES = [
  { value: 'zerodha',    label: 'Indian Stocks / Indices (Zerodha)' },
  { value: 'upstox',     label: 'Indian Stocks / Indices (Upstox)' },
  { value: 'twelve_data',label: 'Global Indices / Commodities' },
  { value: 'fred',       label: 'US M2 / FRED Series' },
]

const TIMEFRAMES: Timeframe[] = ['1M', '3M', '6M', '1Y', '3Y', '5Y']

interface AssetPickerProps {
  label: string
  value: AssetSpec | null
  onChange: (a: AssetSpec) => void
}

function AssetPicker({ label, value, onChange }: AssetPickerProps) {
  const [source, setSource] = useState<string>('zerodha')
  const [query, setQuery]   = useState('')
  const [results, setResults] = useState<InstrumentResult[]>([])
  const [popular, setPopular] = useState<InstrumentResult[]>([])
  const [open, setOpen]     = useState(false)
  const debounce            = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    getPopularInstruments().then((p) => {
      const all = [...p.indian, ...p.global, ...p.fred]
      setPopular(all)
    }).catch(() => {})
  }, [])

  const handleQuery = (q: string) => {
    setQuery(q)
    setOpen(true)
    if (debounce.current) clearTimeout(debounce.current)
    if (q.length < 1) {
      setResults([])
      return
    }
    debounce.current = setTimeout(async () => {
      try {
        const res = await searchInstruments(q)
        setResults(res)
      } catch {
        setResults([])
      }
    }, 350)
  }

  const pick = (item: InstrumentResult) => {
    onChange({ source: item.source as AssetSpec['source'], key: item.key, label: item.label })
    setQuery(item.label)
    setOpen(false)
  }

  const displayed = query.length > 0 ? results : popular.filter(
    (p) => source === 'zerodha' || source === 'upstox'
      ? (p.source === 'zerodha' || p.source === 'upstox')
      : p.source === source
  )

  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 11, color: '#787b86', marginBottom: 4 }}>{label}</div>
      <select
        value={source}
        onChange={(e) => { setSource(e.target.value); setQuery(''); setResults([]) }}
        style={{ width: '100%', marginBottom: 6 }}
      >
        {SOURCES.map((s) => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>

      <div style={{ position: 'relative' }}>
        <input
          value={query}
          onChange={(e) => handleQuery(e.target.value)}
          onFocus={() => setOpen(true)}
          placeholder="Search symbol…"
          style={{ width: '100%' }}
          autoComplete="off"
        />
        {open && displayed.length > 0 && (
          <div style={{
            position: 'absolute',
            zIndex: 100,
            top: '100%',
            left: 0,
            right: 0,
            background: '#1e222d',
            border: '1px solid #2a2e39',
            borderRadius: 4,
            maxHeight: 220,
            overflowY: 'auto',
          }}>
            {displayed.slice(0, 20).map((item) => (
              <div
                key={item.key}
                onMouseDown={() => pick(item)}
                style={{
                  padding: '8px 12px',
                  cursor: 'pointer',
                  fontSize: 13,
                  borderBottom: '1px solid #2a2e39',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = '#2a2e39')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
                <strong>{item.label}</strong>
                <span style={{ color: '#787b86', marginLeft: 8, fontSize: 11 }}>{item.key}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {value && (
        <div style={{ marginTop: 4, fontSize: 11, color: '#26a69a' }}>
          Selected: <strong>{value.label || value.key}</strong>
        </div>
      )}
    </div>
  )
}

export default function RatioBuilder() {
  const {
    builderAssetA, builderAssetB,
    setBuilderAssetA, setBuilderAssetB,
    setChartData, setChartLoading, setChartError,
    timeframe, setTimeframe,
    setActiveItem, watchlist, setWatchlist,
  } = useAppStore()

  const [saving, setSaving] = useState(false)
  const [saveName, setSaveName] = useState('')
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [buildSuccess, setBuildSuccess] = useState(false)

  const handleBuild = async () => {
    if (!builderAssetA || !builderAssetB) return
    setChartLoading(true)
    setChartError(null)
    setBuildSuccess(false)
    try {
      const data = await calculateRatio(builderAssetA, builderAssetB, timeframe)
      setChartData(data)
      setBuildSuccess(true)
      // Clear active watchlist item so chart panel shows builder result
      setActiveItem(null)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to calculate ratio'
      setChartError(msg)
    } finally {
      setChartLoading(false)
    }
  }

  const handleSave = async () => {
    if (!builderAssetA || !builderAssetB || !saveName.trim()) return
    setSaving(true)
    try {
      await addToWatchlist(saveName.trim(), builderAssetA, builderAssetB)
      // Refresh watchlist
      const { getWatchlist } = await import('@/lib/api')
      const items = await getWatchlist()
      setWatchlist(items)
      setShowSaveDialog(false)
      setSaveName('')
    } catch {
      alert('Failed to save to watchlist')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <h3 style={{ fontSize: 14, fontWeight: 600, color: '#d1d4dc' }}>Build Ratio Chart</h3>

      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <AssetPicker label="Asset A (Numerator)" value={builderAssetA} onChange={setBuilderAssetA} />

        <div style={{
          fontSize: 28,
          fontWeight: 700,
          color: '#787b86',
          alignSelf: 'center',
          marginTop: 20,
          flexShrink: 0,
        }}>÷</div>

        <AssetPicker label="Asset B (Denominator)" value={builderAssetB} onChange={setBuilderAssetB} />
      </div>

      {/* Timeframe */}
      <div>
        <div style={{ fontSize: 11, color: '#787b86', marginBottom: 6 }}>Timeframe</div>
        <div style={{ display: 'flex', gap: 6 }}>
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={timeframe === tf ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '5px 12px', fontSize: 12 }}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button
          className="btn-primary"
          onClick={handleBuild}
          disabled={!builderAssetA || !builderAssetB}
          style={{ flex: 1 }}
        >
          Build Chart
        </button>
        {buildSuccess && (
          <button
            className="btn-secondary"
            onClick={() => setShowSaveDialog(true)}
          >
            Save to Watchlist
          </button>
        )}
      </div>

      {/* Save dialog */}
      {showSaveDialog && (
        <div style={{
          background: '#1e222d',
          border: '1px solid #2a2e39',
          borderRadius: 6,
          padding: 12,
          display: 'flex',
          gap: 8,
        }}>
          <input
            value={saveName}
            onChange={(e) => setSaveName(e.target.value)}
            placeholder="Name this ratio (e.g. Nifty / Gold)"
            style={{ flex: 1 }}
            autoFocus
            onKeyDown={(e) => e.key === 'Enter' && handleSave()}
          />
          <button className="btn-primary" onClick={handleSave} disabled={saving || !saveName.trim()}>
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button className="btn-secondary" onClick={() => setShowSaveDialog(false)}>Cancel</button>
        </div>
      )}
    </div>
  )
}
