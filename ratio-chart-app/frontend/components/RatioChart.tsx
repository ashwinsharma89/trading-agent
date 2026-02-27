'use client'

import { useEffect, useRef, useCallback } from 'react'
import {
  createChart,
  IChartApi,
  ISeriesApi,
  LineData,
  CrosshairMode,
  LineSeries,
} from 'lightweight-charts'
import type { RatioChartData } from '@/lib/api'

interface Props {
  data: RatioChartData
  showZscore: boolean
  showRsi: boolean
  assetALabel: string
  assetBLabel: string
}

const CHART_BG    = '#131722'
const GRID_COLOR  = '#1e222d'
const TEXT_COLOR  = '#787b86'
const GREEN       = '#26a69a'
const RED         = '#ef5350'
const YELLOW      = '#f7c948'
const BLUE        = '#2962ff'

function makeChartOpts(height: number) {
  return {
    layout:  { background: { color: CHART_BG }, textColor: TEXT_COLOR, fontSize: 11 },
    grid:    { vertLines: { color: GRID_COLOR }, horzLines: { color: GRID_COLOR } },
    crosshair: { mode: CrosshairMode.Normal },
    rightPriceScale: { borderColor: GRID_COLOR },
    timeScale: { borderColor: GRID_COLOR, timeVisible: true },
    height,
  } as const
}

export default function RatioChart({
  data,
  showZscore,
  showRsi,
  assetALabel,
  assetBLabel,
}: Props) {
  const mainRef    = useRef<HTMLDivElement>(null)
  const zscoreRef  = useRef<HTMLDivElement>(null)
  const rsiRef     = useRef<HTMLDivElement>(null)

  const mainChart    = useRef<IChartApi | null>(null)
  const zscoreChart  = useRef<IChartApi | null>(null)
  const rsiChart     = useRef<IChartApi | null>(null)

  const cleanup = useCallback(() => {
    mainChart.current?.remove()
    zscoreChart.current?.remove()
    rsiChart.current?.remove()
    mainChart.current = null
    zscoreChart.current = null
    rsiChart.current = null
  }, [])

  useEffect(() => {
    if (!mainRef.current) return
    cleanup()

    // ── Main ratio chart ────────────────────────────────────────────────────
    const main = createChart(mainRef.current, makeChartOpts(280))
    mainChart.current = main

    const ratioSeries = main.addSeries(LineSeries, {
      color: BLUE,
      lineWidth: 2,
      title: `${assetALabel} / ${assetBLabel}`,
    })
    ratioSeries.setData(data.ratio as LineData[])
    main.timeScale().fitContent()

    // ── Z-score chart ───────────────────────────────────────────────────────
    if (showZscore && zscoreRef.current) {
      const zc = createChart(zscoreRef.current, makeChartOpts(160))
      zscoreChart.current = zc

      const zSeries = zc.addSeries(LineSeries, {
        color: YELLOW,
        lineWidth: 1.5,
        title: 'Z-Score',
      })
      zSeries.setData(data.zscore as LineData[])

      // Horizontal bands at ±2, ±1, 0
      const bands = [
        { price:  2, color: RED,   style: 2, label: '+2σ' },
        { price:  1, color: RED,   style: 3, label: '+1σ' },
        { price:  0, color: TEXT_COLOR, style: 0, label: '0' },
        { price: -1, color: GREEN, style: 3, label: '-1σ' },
        { price: -2, color: GREEN, style: 2, label: '-2σ' },
      ]
      for (const b of bands) {
        zSeries.createPriceLine({
          price: b.price,
          color: b.color,
          lineWidth: 1,
          lineStyle: b.style,
          axisLabelVisible: true,
          title: b.label,
        })
      }
      zc.timeScale().fitContent()
    }

    // ── RSI chart ────────────────────────────────────────────────────────────
    if (showRsi && rsiRef.current) {
      const rc = createChart(rsiRef.current, makeChartOpts(140))
      rsiChart.current = rc

      const rsiSeries = rc.addSeries(LineSeries, {
        color: YELLOW,
        lineWidth: 1.5,
        title: 'RSI(14)',
      })
      rsiSeries.setData(data.rsi as LineData[])

      for (const level of [{ p: 70, c: RED }, { p: 50, c: TEXT_COLOR }, { p: 30, c: GREEN }]) {
        rsiSeries.createPriceLine({
          price: level.p,
          color: level.c,
          lineWidth: 1,
          lineStyle: level.p === 50 ? 0 : 2,
          axisLabelVisible: true,
          title: String(level.p),
        })
      }
      rc.timeScale().fitContent()
    }

    // ── Sync crosshairs ──────────────────────────────────────────────────────
    const syncCharts = [zscoreChart.current, rsiChart.current].filter(Boolean) as IChartApi[]

    main.subscribeCrosshairMove((param) => {
      if (!param?.time) return
      for (const c of syncCharts) {
        c.setCrosshairPosition(0, param.time, c.addSeries(LineSeries, { visible: false }))
      }
    })

    // Resize observer
    const ro = new ResizeObserver(() => {
      if (mainRef.current) main.applyOptions({ width: mainRef.current.clientWidth })
      if (showZscore && zscoreRef.current && zscoreChart.current)
        zscoreChart.current.applyOptions({ width: zscoreRef.current.clientWidth })
      if (showRsi && rsiRef.current && rsiChart.current)
        rsiChart.current.applyOptions({ width: rsiRef.current.clientWidth })
    })
    if (mainRef.current) ro.observe(mainRef.current)

    return () => {
      ro.disconnect()
      cleanup()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, showZscore, showRsi])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4, width: '100%' }}>
      <div ref={mainRef} style={{ width: '100%' }} />
      {showZscore && <div ref={zscoreRef} style={{ width: '100%' }} />}
      {showRsi    && <div ref={rsiRef}    style={{ width: '100%' }} />}
    </div>
  )
}
