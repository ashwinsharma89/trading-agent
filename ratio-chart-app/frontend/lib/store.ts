import { create } from 'zustand'
import type { WatchlistItem, RatioChartData, AssetSpec, Timeframe } from './api'

interface AppState {
  // Watchlist
  watchlist: WatchlistItem[]
  setWatchlist: (items: WatchlistItem[]) => void

  // Active chart
  activeItem: WatchlistItem | null
  setActiveItem: (item: WatchlistItem | null) => void

  // Chart data
  chartData: RatioChartData | null
  setChartData: (data: RatioChartData | null) => void
  chartLoading: boolean
  setChartLoading: (v: boolean) => void
  chartError: string | null
  setChartError: (e: string | null) => void

  // Timeframe
  timeframe: Timeframe
  setTimeframe: (tf: Timeframe) => void

  // Chart panel toggles
  showZscore: boolean
  setShowZscore: (v: boolean) => void
  showRsi: boolean
  setShowRsi: (v: boolean) => void

  // Ratio builder
  builderAssetA: AssetSpec | null
  builderAssetB: AssetSpec | null
  setBuilderAssetA: (a: AssetSpec | null) => void
  setBuilderAssetB: (b: AssetSpec | null) => void

  // Zerodha auth banner
  zerodhaAuthRequired: boolean
  setZerodhaAuthRequired: (v: boolean) => void
  usingFallback: boolean
  setUsingFallback: (v: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  watchlist: [],
  setWatchlist: (items) => set({ watchlist: items }),

  activeItem: null,
  setActiveItem: (item) => set({ activeItem: item }),

  chartData: null,
  setChartData: (data) => set({ chartData: data }),
  chartLoading: false,
  setChartLoading: (v) => set({ chartLoading: v }),
  chartError: null,
  setChartError: (e) => set({ chartError: e }),

  timeframe: '1Y',
  setTimeframe: (tf) => set({ timeframe: tf }),

  showZscore: true,
  setShowZscore: (v) => set({ showZscore: v }),
  showRsi: true,
  setShowRsi: (v) => set({ showRsi: v }),

  builderAssetA: null,
  builderAssetB: null,
  setBuilderAssetA: (a) => set({ builderAssetA: a }),
  setBuilderAssetB: (b) => set({ builderAssetB: b }),

  zerodhaAuthRequired: false,
  setZerodhaAuthRequired: (v) => set({ zerodhaAuthRequired: v }),
  usingFallback: false,
  setUsingFallback: (v) => set({ usingFallback: v }),
}))
