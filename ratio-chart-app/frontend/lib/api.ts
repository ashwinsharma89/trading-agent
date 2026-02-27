import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

// ── Types ─────────────────────────────────────────────────────────────────────

export interface AssetSpec {
  source: 'zerodha' | 'upstox' | 'twelve_data' | 'fred'
  key: string
  label?: string
}

export interface ChartPoint {
  time: string
  value: number
}

export interface RatioChartData {
  ratio: ChartPoint[]
  zscore: ChartPoint[]
  rsi: ChartPoint[]
  signal: 'overbought' | 'oversold' | 'neutral'
  current_value: number
  current_zscore: number
  pct_change_1w: number | null
  pct_change_1m: number | null
  pct_change_3m: number | null
  asset_a_label: string
  asset_b_label: string
  note: string | null
}

export interface WatchlistItem {
  id: number
  name: string
  asset_a: AssetSpec
  asset_b: AssetSpec
  created_at: string
  current_value?: number
  current_zscore?: number
  signal?: string
  pct_change_1w?: number | null
}

export interface Alert {
  id: number
  name: string
  asset_a: AssetSpec
  asset_b: AssetSpec
  condition: string
  threshold: number
  notify_via: string
  is_active: boolean
  triggered_at: string | null
  created_at: string
}

export interface InstrumentResult {
  key: string
  label: string
  source: string
  exchange?: string
  instrument_type?: string
}

export interface SectorData {
  name: string
  key: string
  current_zscore: number | null
  current_value: number
  signal: string
  pct_change_1w: number | null
}

export type Timeframe = '1M' | '3M' | '6M' | '1Y' | '3Y' | '5Y'

// ── API calls ─────────────────────────────────────────────────────────────────

export async function calculateRatio(
  asset_a: AssetSpec,
  asset_b: AssetSpec,
  timeframe: Timeframe
): Promise<RatioChartData> {
  const { data } = await api.post('/api/ratio/calculate', { asset_a, asset_b, timeframe })
  return data
}

export async function getWatchlist(): Promise<WatchlistItem[]> {
  const { data } = await api.get('/api/ratio/watchlist')
  return data.items
}

export async function addToWatchlist(
  name: string,
  asset_a: AssetSpec,
  asset_b: AssetSpec
): Promise<{ id: number }> {
  const { data } = await api.post('/api/ratio/watchlist', { name, asset_a, asset_b })
  return data
}

export async function removeFromWatchlist(id: number): Promise<void> {
  await api.delete(`/api/ratio/watchlist/${id}`)
}

export async function searchInstruments(q: string): Promise<InstrumentResult[]> {
  const { data } = await api.get('/api/instruments/search', { params: { q } })
  return data.results
}

export async function getPopularInstruments(): Promise<{
  indian: InstrumentResult[]
  global: InstrumentResult[]
  fred: InstrumentResult[]
}> {
  const { data } = await api.get('/api/instruments/popular')
  return data
}

export async function getSectorHeatmap(): Promise<SectorData[]> {
  const { data } = await api.get('/api/sector-heatmap')
  return data.sectors
}

export async function getAlerts(): Promise<Alert[]> {
  const { data } = await api.get('/api/alerts')
  return data.alerts
}

export async function createAlert(payload: {
  name: string
  asset_a: AssetSpec
  asset_b: AssetSpec
  condition: string
  threshold: number
}): Promise<{ id: number }> {
  const { data } = await api.post('/api/alerts', payload)
  return data
}

export async function deleteAlert(id: number): Promise<void> {
  await api.delete(`/api/alerts/${id}`)
}

export async function getZerodhaAuthStatus(): Promise<{
  token_configured: boolean
  source: string
  message: string | null
}> {
  const { data } = await api.get('/auth/zerodha/status')
  return data
}
