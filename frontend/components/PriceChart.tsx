"use client";

import { AreaSeries, BarSeries, CandlestickSeries, ColorType, createChart, createSeriesMarkers, CrosshairMode, HistogramSeries, IChartApi, IPriceScaleApi, LineSeries, LineStyle, PriceScaleMode, UTCTimestamp } from "lightweight-charts";
import { useEffect, useMemo, useRef, useState } from "react";
import { detectPatternOverlays, PatternCandle } from "../lib/patterns";

type Bar = { trading_date?: string; timestamp?: string; open: string | number; high: string | number; low: string | number; close: string | number; volume: number };
type Interval = "5m" | "15m" | "30m" | "1h" | "4h" | "1D" | "1W" | "1M";
type RangePreset = "1D" | "5D" | "1M" | "3M" | "6M" | "YTD" | "1Y" | "5Y" | "MAX" | "CUSTOM";
type ChartStyle = "candles" | "bars" | "line" | "area";
type ScaleMode = "normal" | "log" | "percent" | "indexed";
type Indicator = "SMA20" | "SMA50" | "SMA100" | "SMA200" | "EMA20" | "EMA50" | "EMA200" | "BB" | "VWAP" | "RSI" | "MACD" | "STOCH" | "ATR";
type ChartBar = { time: string | UTCTimestamp; open: number; high: number; low: number; close: number; volume: number };
type Legend = { time: string; open: number; high: number; low: number; close: number; volume: number } | null;
type DrawingTool = "cursor" | "trend" | "horizontal" | "path" | "fib" | "brush" | "text" | "emoji" | "ruler";
type DrawingPoint = { time: ChartBar["time"]; price: number };
type Drawing = { id: string; tool: Exclude<DrawingTool, "cursor">; points: DrawingPoint[]; color: string; text?: string };
const intradayTimeframes: Partial<Record<Interval, string>> = { "5m": "5Min", "15m": "15Min", "30m": "30Min", "1h": "1Hour", "4h": "4Hour" };
const rangeOptions: RangePreset[] = ["1D", "5D", "1M", "3M", "6M", "YTD", "1Y", "5Y", "MAX"];
const indicatorOptions: { id: Indicator; label: string; group: "Overlay" | "Oscillator" }[] = [
  { id: "SMA20", label: "SMA 20", group: "Overlay" }, { id: "SMA50", label: "SMA 50", group: "Overlay" },
  { id: "SMA100", label: "SMA 100", group: "Overlay" }, { id: "SMA200", label: "SMA 200", group: "Overlay" },
  { id: "EMA20", label: "EMA 20", group: "Overlay" }, { id: "EMA50", label: "EMA 50", group: "Overlay" },
  { id: "EMA200", label: "EMA 200", group: "Overlay" }, { id: "BB", label: "Bollinger Bands", group: "Overlay" },
  { id: "VWAP", label: "VWAP", group: "Overlay" }, { id: "RSI", label: "RSI 14", group: "Oscillator" },
  { id: "MACD", label: "MACD 12/26/9", group: "Oscillator" }, { id: "STOCH", label: "Stochastic 14/3", group: "Oscillator" },
  { id: "ATR", label: "ATR 14", group: "Oscillator" },
];
const scaleModes: Record<ScaleMode, PriceScaleMode> = { normal: PriceScaleMode.Normal, log: PriceScaleMode.Logarithmic, percent: PriceScaleMode.Percentage, indexed: PriceScaleMode.IndexedTo100 };

function timeMs(value: string | number) { return typeof value === "number" ? value * 1000 : Date.parse(`${value}T00:00:00Z`); }

function bucket(date: string, interval: Interval) {
  if (interval === "1D") return date;
  const value = new Date(`${date}T00:00:00Z`);
  if (interval === "1W") {
    const day = value.getUTCDay() || 7;
    value.setUTCDate(value.getUTCDate() - day + 1);
    return value.toISOString().slice(0, 10);
  }
  return `${date.slice(0, 7)}-01`;
}

function aggregate(input: Bar[], interval: Interval) {
  const ordered = input.slice().sort((a, b) => (a.trading_date ?? a.timestamp ?? "").localeCompare(b.trading_date ?? b.timestamp ?? ""));
  const output: any[] = [];
  for (const bar of ordered) {
    if (!bar.trading_date) continue;
    const time = bucket(bar.trading_date, interval);
    const current = output.at(-1);
    if (!current || current.time !== time) {
      output.push({ time, open: +bar.open, high: +bar.high, low: +bar.low, close: +bar.close, volume: +bar.volume });
    } else {
      current.high = Math.max(current.high, +bar.high);
      current.low = Math.min(current.low, +bar.low);
      current.close = +bar.close;
      current.volume += +bar.volume;
    }
  }
  return output;
}

function normalizeIntraday(input: Bar[]) {
  return input.slice().sort((a, b) => (a.timestamp ?? "").localeCompare(b.timestamp ?? "")).map((bar) => ({
    time: Math.floor(Date.parse(bar.timestamp!)/1000) as UTCTimestamp,
    open: +bar.open, high: +bar.high, low: +bar.low, close: +bar.close, volume: +bar.volume,
  }));
}

function movingAverage(data: ChartBar[], length: number) {
  let sum = 0;
  return data.flatMap((bar, index) => {
    sum += bar.close;
    if (index >= length) sum -= data[index - length].close;
    return index >= length - 1 ? [{ time: bar.time, value: sum / length }] : [];
  });
}

function exponentialValues(values: number[], length: number) {
  const multiplier = 2 / (length + 1); let previous = values[0] ?? 0;
  return values.map((value, index) => previous = index === 0 ? value : value * multiplier + previous * (1 - multiplier));
}

function exponentialAverage(data: ChartBar[], length: number) {
  const values = exponentialValues(data.map((bar) => bar.close), length);
  return data.map((bar, index) => ({ time: bar.time, value: values[index] })).slice(length - 1);
}

function bollingerBands(data: ChartBar[], length = 20) {
  const middle = movingAverage(data, length);
  return middle.map((point, index) => {
    const sourceIndex = index + length - 1;
    const window = data.slice(sourceIndex - length + 1, sourceIndex + 1);
    const deviation = Math.sqrt(window.reduce((sum, bar) => sum + (bar.close - point.value) ** 2, 0) / length);
    return { time: point.time, middle: point.value, upper: point.value + deviation * 2, lower: point.value - deviation * 2 };
  });
}

function vwap(data: ChartBar[]) {
  let day = "", totalVolume = 0, totalValue = 0;
  return data.map((bar) => {
    const key = typeof bar.time === "string" ? bar.time.slice(0, 10) : new Date(bar.time * 1000).toISOString().slice(0, 10);
    if (key !== day) { day = key; totalVolume = 0; totalValue = 0; }
    totalVolume += bar.volume; totalValue += ((bar.high + bar.low + bar.close) / 3) * bar.volume;
    return { time: bar.time, value: totalVolume ? totalValue / totalVolume : bar.close };
  });
}

function rsi(data: ChartBar[], length = 14) {
  let gain = 0, loss = 0; const output: { time: ChartBar["time"]; value: number }[] = [];
  for (let index = 1; index < data.length; index++) {
    const change = data[index].close - data[index - 1].close;
    if (index <= length) { gain += Math.max(change, 0); loss += Math.max(-change, 0); }
    if (index === length) { gain /= length; loss /= length; }
    else if (index > length) { gain = (gain * (length - 1) + Math.max(change, 0)) / length; loss = (loss * (length - 1) + Math.max(-change, 0)) / length; }
    if (index >= length) output.push({ time: data[index].time, value: loss === 0 ? 100 : 100 - 100 / (1 + gain / loss) });
  }
  return output;
}

function macd(data: ChartBar[]) {
  const closes = data.map((bar) => bar.close), fast = exponentialValues(closes, 12), slow = exponentialValues(closes, 26);
  const values = closes.map((_, index) => fast[index] - slow[index]); const signal = exponentialValues(values, 9);
  return data.map((bar, index) => ({ time: bar.time, value: values[index], signal: signal[index], histogram: values[index] - signal[index] })).slice(25);
}

function stochastic(data: ChartBar[], length = 14) {
  const raw = data.map((bar, index) => {
    const window = data.slice(Math.max(0, index - length + 1), index + 1);
    const high = Math.max(...window.map((item) => item.high)), low = Math.min(...window.map((item) => item.low));
    return high === low ? 50 : ((bar.close - low) / (high - low)) * 100;
  });
  const smooth = raw.map((_, index) => raw.slice(Math.max(0, index - 2), index + 1).reduce((sum, value) => sum + value, 0) / Math.min(index + 1, 3));
  return data.map((bar, index) => ({ time: bar.time, k: raw[index], d: smooth[index] })).slice(length - 1);
}

function averageTrueRange(data: ChartBar[], length = 14) {
  const ranges = data.map((bar, index) => index === 0 ? bar.high - bar.low : Math.max(bar.high - bar.low, Math.abs(bar.high - data[index - 1].close), Math.abs(bar.low - data[index - 1].close)));
  const values = exponentialValues(ranges, length);
  return data.map((bar, index) => ({ time: bar.time, value: values[index] })).slice(length - 1);
}

function isRegularSession(bar: ChartBar) {
  if (typeof bar.time === "string") return true;
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date(bar.time * 1000));
  const hour = Number(parts.find((part) => part.type === "hour")?.value), minute = Number(parts.find((part) => part.type === "minute")?.value);
  const clock = hour * 60 + minute; return clock >= 570 && clock < 960;
}

function formatChartTime(time: ChartBar["time"]) {
  return new Date(typeof time === "string" ? `${time}T00:00:00Z` : time * 1000).toLocaleString([], { dateStyle: "medium", timeStyle: typeof time === "string" ? undefined : "short" });
}

function PanelIcon({ open }: { open: boolean }) {
  return <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M16 4v16"/>{!open && <path d="m14 9 4 3-4 3"/>}</svg>;
}

function ExpandIcon({ expanded }: { expanded: boolean }) {
  return expanded
    ? <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M9 3v6H3M15 3v6h6M9 21v-6H3M15 21v-6h6"/></svg>
    : <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M8 3H3v5M16 3h5v5M8 21H3v-5M16 21h5v-5"/></svg>;
}

function DrawingIcon({ name }: { name: DrawingTool | "zoom" | "magnet" | "lock" | "eye" | "trash" }) {
  const common = { fill: "none", stroke: "currentColor", strokeWidth: 1.7, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  if (name === "trend") return <svg viewBox="0 0 24 24" {...common}><path d="m5 17 14-12"/><circle cx="5" cy="17" r="2"/><circle cx="19" cy="5" r="2"/></svg>;
  if (name === "horizontal") return <svg viewBox="0 0 24 24" {...common}><path d="M4 12h16"/><circle cx="6" cy="12" r="2"/></svg>;
  if (name === "path") return <svg viewBox="0 0 24 24" {...common}><path d="m4 17 4-10 5 8 3-10 4 12"/><circle cx="4" cy="17" r="1.5"/><circle cx="8" cy="7" r="1.5"/><circle cx="13" cy="15" r="1.5"/><circle cx="16" cy="5" r="1.5"/><circle cx="20" cy="17" r="1.5"/></svg>;
  if (name === "fib") return <svg viewBox="0 0 24 24" {...common}><path d="M5 5v14M5 7h14M5 11h10M5 15h14M5 19h8"/><circle cx="5" cy="7" r="1.3"/></svg>;
  if (name === "brush") return <svg viewBox="0 0 24 24" {...common}><path d="M4 18c4-8 6-10 9-8s3 4 7-4M4 18c2 1 4 1 6 0"/></svg>;
  if (name === "text") return <svg viewBox="0 0 24 24" {...common}><path d="M5 6V4h14v2M12 4v16M8 20h8"/></svg>;
  if (name === "emoji") return <svg viewBox="0 0 24 24" {...common}><circle cx="12" cy="12" r="9"/><path d="M8 10h.01M16 10h.01M8 14c2.5 3 5.5 3 8 0"/></svg>;
  if (name === "ruler") return <svg viewBox="0 0 24 24" {...common}><path d="m4 16 12-12 4 4L8 20zM9 11l2 2M12 8l2 2M6 14l2 2"/></svg>;
  if (name === "zoom") return <svg viewBox="0 0 24 24" {...common}><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5M10 7v6M7 10h6"/></svg>;
  if (name === "magnet") return <svg viewBox="0 0 24 24" {...common}><path d="M6 4v9a6 6 0 0 0 12 0V4h-4v9a2 2 0 0 1-4 0V4zM6 8h4M14 8h4"/></svg>;
  if (name === "lock") return <svg viewBox="0 0 24 24" {...common}><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 7-2M12 14v2"/></svg>;
  if (name === "eye") return <svg viewBox="0 0 24 24" {...common}><path d="M3 12s3-5 9-5 9 5 9 5-3 5-9 5-9-5-9-5z"/><circle cx="12" cy="12" r="2.5"/></svg>;
  if (name === "trash") return <svg viewBox="0 0 24 24" {...common}><path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13M10 11v5M14 11v5"/></svg>;
  return <svg viewBox="0 0 24 24" {...common}><path d="m5 4 13 9-6 1-3 6z"/></svg>;
}

export default function PriceChart({ bars, instrumentId, apiBase, expanded = false, onToggleExpanded, tradeCasesOpen = true, onToggleTradeCases }: { bars: Bar[]; instrumentId: number; apiBase: string; expanded?: boolean; onToggleExpanded?: () => void; tradeCasesOpen?: boolean; onToggleTradeCases?: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const priceSeriesRef = useRef<any>(null);
  const priceScaleRef = useRef<IPriceScaleApi | null>(null);
  const [interval, setInterval] = useState<Interval>("1D");
  const [intraday, setIntraday] = useState<Record<string, Bar[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedPatterns, setSelectedPatterns] = useState<string[]>([]);
  const [showPatternLabels, setShowPatternLabels] = useState(false);
  const [range, setRange] = useState<RangePreset>("1Y");
  const [showCustomRange, setShowCustomRange] = useState(false);
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");
  const [chartStyle, setChartStyle] = useState<ChartStyle>("candles");
  const [scaleMode, setScaleMode] = useState<ScaleMode>("normal");
  const [indicators, setIndicators] = useState<Indicator[]>(["SMA20"]);
  const [regularSessionOnly, setRegularSessionOnly] = useState(true);
  const [legend, setLegend] = useState<Legend>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [drawingTool, setDrawingTool] = useState<DrawingTool>("cursor");
  const [drawingsByInterval, setDrawingsByInterval] = useState<Partial<Record<Interval, Drawing[]>>>({});
  const [draftPoints, setDraftPoints] = useState<DrawingPoint[]>([]);
  const [previewPoint, setPreviewPoint] = useState<DrawingPoint | null>(null);
  const [drawingsVisible, setDrawingsVisible] = useState(true);
  const [drawingsLocked, setDrawingsLocked] = useState(false);
  const [magnetEnabled, setMagnetEnabled] = useState(true);
  const [, setDrawingViewport] = useState(0);
  const timeframe = intradayTimeframes[interval];
  const rawData = useMemo(() => timeframe ? normalizeIntraday(intraday[timeframe] ?? []) : aggregate(bars ?? [], interval), [bars, interval, intraday, timeframe]);
  const data = useMemo(() => timeframe && regularSessionOnly ? rawData.filter(isRegularSession) : rawData, [rawData, regularSessionOnly, timeframe]);
  const visibleData = useMemo(() => {
    if (!data.length || range === "MAX") return data;
    const last = timeMs(data.at(-1).time); let start = 0; let end = last;
    if (range === "CUSTOM") {
      start = customStart ? Date.parse(`${customStart}T00:00:00Z`) : 0;
      end = customEnd ? Date.parse(`${customEnd}T23:59:59Z`) : last;
    } else if (range === "YTD") {
      const date = new Date(last); start = Date.UTC(date.getUTCFullYear(), 0, 1);
    } else {
      const days: Record<string, number> = { "1D": 1, "5D": 5, "1M": 31, "3M": 92, "6M": 183, "1Y": 366, "5Y": 365 * 5 + 2 };
      start = last - days[range] * 86_400_000;
    }
    return data.filter((bar: any) => { const value = timeMs(bar.time); return value >= start && value <= end; });
  }, [customEnd, customStart, data, range]);
  const patternOverlays = useMemo(() => detectPatternOverlays(visibleData as PatternCandle[]), [visibleData]);
  const drawings = drawingsByInterval[interval] ?? [];

  useEffect(() => { setSelectedPatterns(patternOverlays.map((pattern) => pattern.id)); }, [patternOverlays]);

  const loadIntraday = async (selectedTimeframe: string, force = false) => {
    if (!force && intraday[selectedTimeframe]) return;
    setLoading(!force); setRefreshing(force); setError("");
    try {
      const response = await fetch(`${apiBase}/api/v1/instruments/${instrumentId}/intraday/?timeframe=${selectedTimeframe}`, { cache: "no-store" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Intraday prices are unavailable");
      setIntraday((current) => ({ ...current, [selectedTimeframe]: payload }));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Intraday prices are unavailable"); }
    finally { setLoading(false); setRefreshing(false); }
  };

  useEffect(() => {
    if (!timeframe || intraday[timeframe]) return;
    void loadIntraday(timeframe);
  }, [apiBase, instrumentId, intraday, timeframe]);

  useEffect(() => {
    if (!timeframe) return;
    const timer = window.setInterval(() => { if (!document.hidden) void loadIntraday(timeframe, true); }, 60_000);
    return () => window.clearInterval(timer);
  }, [timeframe, apiBase, instrumentId]);

  useEffect(() => {
    if (!ref.current || !visibleData.length) return;
    const chart = createChart(ref.current, {
      height: expanded ? Math.max(window.innerHeight - 205, 640) : 560,
      autoSize: true,
      layout: { background: { type: ColorType.Solid, color: "#091210" }, textColor: "#8da49a", panes: { enableResize: true, separatorColor: "#1c312b", separatorHoverColor: "#50f2a766" } },
      grid: { vertLines: { color: "#13231e" }, horzLines: { color: "#13231e" } },
      crosshair: { mode: CrosshairMode.MagnetOHLC, vertLine: { color: "#789087", labelBackgroundColor: "#16352b" }, horzLine: { color: "#789087", labelBackgroundColor: "#16352b" } },
      rightPriceScale: {
        autoScale: true, mode: scaleModes[scaleMode], borderColor: "#1c312b", borderVisible: true, visible: true,
        ticksVisible: true, minimumWidth: 82, entireTextOnly: true,
        ensureEdgeTickMarksVisible: true, tickMarkDensity: 1.2,
        scaleMargins: { top: .05, bottom: .08 },
      },
      timeScale: { borderColor: "#1c312b", timeVisible: true },
      handleScale: {
        mouseWheel: true, pinch: true,
        axisPressedMouseMove: { time: true, price: true },
        axisDoubleClickReset: { time: true, price: true },
      },
      handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
    });
    chartRef.current = chart;
    priceScaleRef.current = chart.priceScale("right");
    let priceSeries: any;
    if (chartStyle === "bars") priceSeries = chart.addSeries(BarSeries, { upColor: "#39dfa0", downColor: "#fb7185", thinBars: false, priceFormat: { type: "price", precision: 2, minMove: .01 } });
    else if (chartStyle === "line") priceSeries = chart.addSeries(LineSeries, { color: "#50f2a7", lineWidth: 2, priceFormat: { type: "price", precision: 2, minMove: .01 } });
    else if (chartStyle === "area") priceSeries = chart.addSeries(AreaSeries, { lineColor: "#50f2a7", topColor: "#50f2a755", bottomColor: "#50f2a705", lineWidth: 2, priceFormat: { type: "price", precision: 2, minMove: .01 } });
    else priceSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#39dfa0", downColor: "#fb7185", borderVisible: false, wickUpColor: "#39dfa0", wickDownColor: "#fb7185",
      priceLineVisible: true, lastValueVisible: true, priceFormat: { type: "price", precision: 2, minMove: .01 },
    });
    priceSeriesRef.current = priceSeries;
    priceSeries.setData(chartStyle === "line" || chartStyle === "area" ? visibleData.map((bar) => ({ time: bar.time, value: bar.close })) : visibleData);
    const volume = chart.addSeries(HistogramSeries, { priceFormat: { type: "volume" }, priceScaleId: "volume" });
    chart.priceScale("volume").applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
    volume.setData(visibleData.map((bar) => ({ time: bar.time, value: bar.volume, color: bar.close >= bar.open ? "#39dfa055" : "#fb718555" })));
    const addLine = (points: any[], color: string, title: string, width: 1 | 2 | 3 | 4 = 1, paneIndex = 0) => {
      const series = chart.addSeries(LineSeries, { color, title, lineWidth: width, priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false }, paneIndex);
      series.setData(points); return series;
    };
    if (indicators.includes("SMA20")) addLine(movingAverage(visibleData, 20), "#fbbf24", "SMA 20", 2);
    if (indicators.includes("SMA50")) addLine(movingAverage(visibleData, 50), "#60a5fa", "SMA 50", 2);
    if (indicators.includes("SMA100")) addLine(movingAverage(visibleData, 100), "#2dd4bf", "SMA 100", 2);
    if (indicators.includes("SMA200")) addLine(movingAverage(visibleData, 200), "#f472b6", "SMA 200", 2);
    if (indicators.includes("EMA20")) addLine(exponentialAverage(visibleData, 20), "#c084fc", "EMA 20", 2);
    if (indicators.includes("EMA50")) addLine(exponentialAverage(visibleData, 50), "#a78bfa", "EMA 50", 2);
    if (indicators.includes("EMA200")) addLine(exponentialAverage(visibleData, 200), "#fb7185", "EMA 200", 2);
    if (indicators.includes("VWAP")) addLine(vwap(visibleData), "#fb923c", "VWAP", 2);
    if (indicators.includes("BB")) {
      const bands = bollingerBands(visibleData);
      addLine(bands.map((point) => ({ time: point.time, value: point.upper })), "#38bdf8", "BB upper");
      addLine(bands.map((point) => ({ time: point.time, value: point.middle })), "#38bdf899", "BB basis");
      addLine(bands.map((point) => ({ time: point.time, value: point.lower })), "#38bdf8", "BB lower");
    }
    let paneIndex = 1;
    if (indicators.includes("RSI")) {
      const rsiSeries = addLine(rsi(visibleData), "#c084fc", "RSI 14", 2, paneIndex);
      rsiSeries.createPriceLine({ price: 70, color: "#fb718588", lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: "70" });
      rsiSeries.createPriceLine({ price: 30, color: "#39dfa088", lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: "30" });
      chart.priceScale("right", paneIndex).applyOptions({ scaleMargins: { top: .08, bottom: .08 } }); paneIndex++;
    }
    if (indicators.includes("MACD")) {
      const points = macd(visibleData);
      addLine(points.map((point) => ({ time: point.time, value: point.value })), "#38bdf8", "MACD", 2, paneIndex);
      addLine(points.map((point) => ({ time: point.time, value: point.signal })), "#f59e0b", "Signal", 1, paneIndex);
      const histogram = chart.addSeries(HistogramSeries, { priceLineVisible: false, lastValueVisible: false, priceFormat: { type: "price", precision: 2, minMove: .01 } }, paneIndex);
      histogram.setData(points.map((point) => ({ time: point.time, value: point.histogram, color: point.histogram >= 0 ? "#39dfa077" : "#fb718577" })) as any); paneIndex++;
    }
    if (indicators.includes("STOCH")) {
      const points = stochastic(visibleData);
      const kSeries = addLine(points.map((point) => ({ time: point.time, value: point.k })), "#38bdf8", "%K", 2, paneIndex);
      addLine(points.map((point) => ({ time: point.time, value: point.d })), "#f59e0b", "%D", 1, paneIndex);
      kSeries.createPriceLine({ price: 80, color: "#fb718588", lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: "80" });
      kSeries.createPriceLine({ price: 20, color: "#39dfa088", lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: "20" }); paneIndex++;
    }
    if (indicators.includes("ATR")) { addLine(averageTrueRange(visibleData), "#fbbf24", "ATR 14", 2, paneIndex); paneIndex++; }
    const visiblePatterns = patternOverlays.filter((pattern) => selectedPatterns.includes(pattern.id));
    for (const pattern of visiblePatterns) {
      for (const line of pattern.lines) {
        const series = chart.addSeries(LineSeries, {
          color: pattern.color, lineWidth: 2, lineStyle: LineStyle.Dashed,
          priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false,
        });
        series.setData(line as any);
      }
    }
    const markers = visiblePatterns.filter((pattern) => pattern.marker).map((pattern) => ({
      ...pattern.marker!, text: showPatternLabels ? pattern.marker!.text : "", color: pattern.color, size: showPatternLabels ? 1.35 : 1,
    }));
    if (markers.length) createSeriesMarkers(priceSeries, markers as any);
    const mainPane = chart.panes()[0]; if (mainPane) mainPane.setStretchFactor(4);
    chart.panes().slice(1).forEach((pane) => pane.setStretchFactor(1));
    const crosshairHandler = (param: any) => {
      if (!param.time) { const last = visibleData.at(-1); if (last) setLegend({ ...last, time: formatChartTime(last.time) }); return; }
      const match = visibleData.find((bar) => bar.time === param.time);
      if (match) setLegend({ ...match, time: formatChartTime(match.time) });
    };
    chart.subscribeCrosshairMove(crosshairHandler);
    const drawingRangeHandler = () => setDrawingViewport((value) => value + 1);
    chart.timeScale().subscribeVisibleLogicalRangeChange(drawingRangeHandler);
    const resizeObserver = new ResizeObserver(drawingRangeHandler); resizeObserver.observe(chart.chartElement());
    const latest = visibleData.at(-1); if (latest) setLegend({ ...latest, time: formatChartTime(latest.time) });
    chart.timeScale().fitContent();
    const finishPriceScaleResize = () => {
      const range = priceScaleRef.current?.getVisibleRange();
      if (scaleMode === "normal" && range && range.from < 0) {
        priceScaleRef.current?.setVisibleRange({ from: 0, to: Math.max(range.to, 0.01) });
      }
    };
    chart.chartElement().addEventListener("pointerup", finishPriceScaleResize);
    return () => { resizeObserver.disconnect(); chart.timeScale().unsubscribeVisibleLogicalRangeChange(drawingRangeHandler); chart.chartElement().removeEventListener("pointerup", finishPriceScaleResize); chart.unsubscribeCrosshairMove(crosshairHandler); chartRef.current = null; priceSeriesRef.current = null; priceScaleRef.current = null; chart.remove(); };
  }, [chartStyle, expanded, indicators, patternOverlays, scaleMode, selectedPatterns, showPatternLabels, visibleData]);

  const togglePattern = (id: string) => setSelectedPatterns((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  const zoomPriceScale = (factor: number) => {
    const scale = priceScaleRef.current; const range = scale?.getVisibleRange();
    if (!scale || !range) return;
    const center = (range.from + range.to) / 2; const half = (range.to - range.from) * factor / 2;
    const from = center - half; const to = center + half;
    scale.setVisibleRange(scaleMode === "normal" && from < 0 ? { from: 0, to: to - from } : { from, to });
  };
  const toggleIndicator = (indicator: Indicator) => setIndicators((current) => current.includes(indicator) ? current.filter((item) => item !== indicator) : [...current, indicator]);
  const exportChart = () => {
    const canvas = chartRef.current?.takeScreenshot(true, false); if (!canvas) return;
    const link = document.createElement("a"); link.download = `dragonfly-${interval}-${new Date().toISOString().slice(0, 10)}.png`; link.href = canvas.toDataURL("image/png"); link.click();
  };
  const setTool = (tool: DrawingTool) => { setDrawingTool((current) => current === tool ? "cursor" : tool); setDraftPoints([]); setPreviewPoint(null); };
  const addDrawing = (drawing: Drawing) => setDrawingsByInterval((current) => ({ ...current, [interval]: [...(current[interval] ?? []), drawing] }));
  const drawingPoint = (event: React.PointerEvent<SVGSVGElement>): DrawingPoint | null => {
    const chart = chartRef.current, series = priceSeriesRef.current; if (!chart || !series) return null;
    const rect = event.currentTarget.getBoundingClientRect(), x = event.clientX - rect.left, y = event.clientY - rect.top;
    const logical = chart.timeScale().coordinateToLogical(x); let time: any = chart.timeScale().coordinateToTime(x); let price = series.coordinateToPrice(y);
    if (magnetEnabled && logical !== null) {
      const bar = visibleData[Math.max(0, Math.min(visibleData.length - 1, Math.round(logical)))];
      if (bar) { time = bar.time; const prices = [bar.open, bar.high, bar.low, bar.close]; price = prices.reduce((nearest, value) => Math.abs(value - price) < Math.abs(nearest - price) ? value : nearest, prices[0]); }
    }
    if (time && typeof time === "object") time = `${time.year}-${String(time.month).padStart(2, "0")}-${String(time.day).padStart(2, "0")}`;
    return time != null && price != null ? { time, price } : null;
  };
  const drawingClick = (event: React.PointerEvent<SVGSVGElement>) => {
    if (drawingTool === "cursor" || drawingTool === "brush" || drawingsLocked) return;
    const point = drawingPoint(event); if (!point) return;
    const id = `${drawingTool}-${Date.now()}`, color = "#50f2a7";
    if (drawingTool === "horizontal") { addDrawing({ id, tool: drawingTool, points: [point], color }); return; }
    if (drawingTool === "text" || drawingTool === "emoji") {
      const value = window.prompt(drawingTool === "text" ? "Enter chart note" : "Enter an emoji or marker", drawingTool === "text" ? "Note" : "⭐");
      if (value) addDrawing({ id, tool: drawingTool, points: [point], color, text: value }); return;
    }
    if (drawingTool === "path") { setDraftPoints((current) => [...current, point]); return; }
    if (!draftPoints.length) setDraftPoints([point]);
    else { addDrawing({ id, tool: drawingTool, points: [draftPoints[0], point], color }); setDraftPoints([]); setPreviewPoint(null); }
  };
  const finishPath = () => {
    if (drawingTool === "path" && draftPoints.length >= 2) addDrawing({ id: `path-${Date.now()}`, tool: "path", points: draftPoints, color: "#50f2a7" });
    setDraftPoints([]); setPreviewPoint(null);
  };
  const drawingPointerDown = (event: React.PointerEvent<SVGSVGElement>) => {
    if (drawingTool !== "brush" || drawingsLocked) return; const point = drawingPoint(event); if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId); setDraftPoints([point]);
  };
  const drawingPointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
    if (drawingTool === "cursor" || drawingsLocked) return; const point = drawingPoint(event); if (!point) return;
    if (drawingTool === "brush" && event.currentTarget.hasPointerCapture(event.pointerId)) setDraftPoints((current) => [...current, point]);
    else setPreviewPoint(point);
  };
  const drawingPointerUp = (event: React.PointerEvent<SVGSVGElement>) => {
    if (drawingTool !== "brush" || draftPoints.length < 2) return;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
    addDrawing({ id: `brush-${Date.now()}`, tool: "brush", points: draftPoints, color: "#50f2a7" }); setDraftPoints([]); setPreviewPoint(null);
  };
  const pixelPoint = (point: DrawingPoint) => {
    const x = chartRef.current?.timeScale().timeToCoordinate(point.time as any), y = priceSeriesRef.current?.priceToCoordinate(point.price);
    return x == null || y == null ? null : { x, y };
  };
  const drawingShape = (drawing: Drawing) => {
    const points = drawing.points.map(pixelPoint).filter(Boolean) as { x: number; y: number }[]; if (!points.length) return null;
    if (drawing.tool === "horizontal") return <line key={drawing.id} x1="0" x2="100%" y1={points[0].y} y2={points[0].y} stroke={drawing.color} strokeWidth="1.5" strokeDasharray="5 4"/>;
    if (drawing.tool === "trend") return <g key={drawing.id}><line x1={points[0].x} y1={points[0].y} x2={points[1]?.x ?? points[0].x} y2={points[1]?.y ?? points[0].y} stroke={drawing.color} strokeWidth="2"/><circle cx={points[0].x} cy={points[0].y} r="3" fill="#091210" stroke={drawing.color}/>{points[1] && <circle cx={points[1].x} cy={points[1].y} r="3" fill="#091210" stroke={drawing.color}/>}</g>;
    if (drawing.tool === "path" || drawing.tool === "brush") return <polyline key={drawing.id} points={points.map((point) => `${point.x},${point.y}`).join(" ")} fill="none" stroke={drawing.color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round"/>;
    if (drawing.tool === "fib" && points[1]) return <g key={drawing.id}>{[0, .236, .382, .5, .618, .786, 1].map((level) => { const y = points[0].y + (points[1].y - points[0].y) * level; return <g key={level}><line x1={Math.min(points[0].x, points[1].x)} x2={Math.max(points[0].x, points[1].x)} y1={y} y2={y} stroke={drawing.color} strokeWidth="1" opacity={level === 0 || level === 1 ? 1 : .65}/><text x={Math.max(points[0].x, points[1].x) + 4} y={y - 2} fill={drawing.color} fontSize="9">{level}</text></g>; })}</g>;
    if (drawing.tool === "ruler" && points[1]) { const change = drawing.points[0].price ? ((drawing.points[1].price / drawing.points[0].price) - 1) * 100 : 0; return <g key={drawing.id}><line x1={points[0].x} y1={points[0].y} x2={points[1].x} y2={points[1].y} stroke={drawing.color} strokeWidth="1.5" strokeDasharray="4 3"/><rect x={(points[0].x + points[1].x) / 2 - 30} y={(points[0].y + points[1].y) / 2 - 15} width="60" height="18" rx="4" fill="#07100e" stroke={drawing.color}/><text x={(points[0].x + points[1].x) / 2} y={(points[0].y + points[1].y) / 2 - 3} textAnchor="middle" fill={drawing.color} fontSize="10">{change.toFixed(2)}%</text></g>; }
    if (drawing.tool === "text" || drawing.tool === "emoji") return <text key={drawing.id} x={points[0].x} y={points[0].y} fill={drawing.color} fontSize={drawing.tool === "emoji" ? "22" : "13"} fontWeight="600">{drawing.text}</text>;
    return null;
  };

  return <div className="rounded-2xl border border-[#1c312b] bg-[#091210]">
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#1c312b] px-4 py-2.5">
      <div><p className="text-sm font-bold">Price action</p><p className="text-xs text-[#789087]">{timeframe ? `Alpaca intraday OHLCV · ${regularSessionOnly ? "regular session" : "all sessions"}` : `Complete stored history · ${bars.length.toLocaleString()} daily bars`}</p><p className="mt-1 text-[11px] text-[#50f2a7]">{patternOverlays.length ? `${patternOverlays.length} active pattern${patternOverlays.length === 1 ? "" : "s"} on ${interval}` : `No active pattern on ${interval}`}</p></div>
      <div className="flex flex-wrap items-center justify-end gap-1.5">
        <select aria-label="Chart style" value={chartStyle} onChange={(event) => setChartStyle(event.target.value as ChartStyle)} className="h-8 rounded-md border border-[#29473e] bg-[#050b0a] px-2 text-[11px] font-bold text-[#9eb3aa]"><option value="candles">Candles</option><option value="bars">Bars</option><option value="line">Line</option><option value="area">Area</option></select>
        <details className="group relative z-40">
          <summary className="flex h-8 cursor-pointer list-none items-center gap-1.5 rounded-md border border-[#29473e] bg-[#050b0a] px-2.5 text-[11px] font-bold text-[#9eb3aa] marker:content-none">Indicators <span className="rounded bg-[#16352b] px-1.5 text-[#50f2a7]">{indicators.length}</span><span className="text-[9px] transition group-open:rotate-180">▼</span></summary>
          <div className="absolute right-0 top-10 z-50 w-64 rounded-xl border border-[#29473e] bg-[#07100e] p-3 shadow-2xl shadow-black/60">
            {(["Overlay", "Oscillator"] as const).map((group) => <div key={group} className="mb-3 last:mb-0"><div className="mb-1.5 flex items-center justify-between"><p className="text-[9px] font-black uppercase tracking-[.14em] text-[#60756d]">{group}</p>{group === "Overlay" && indicators.length > 0 && <button onClick={() => setIndicators([])} className="text-[9px] font-bold text-[#789087] hover:text-white">Clear all</button>}</div><div className="grid grid-cols-2 gap-1">{indicatorOptions.filter((item) => item.group === group).map((item) => <button key={item.id} onClick={() => toggleIndicator(item.id)} className={`flex items-center justify-between rounded-md border px-2 py-1.5 text-left text-[10px] font-bold ${indicators.includes(item.id) ? "border-[#50f2a7] bg-[#16352b] text-[#50f2a7]" : "border-[#1c312b] text-[#8da49a]"}`}><span>{item.label}</span><span>{indicators.includes(item.id) ? "✓" : "+"}</span></button>)}</div></div>)}
          </div>
        </details>
        <div className="flex flex-wrap justify-end rounded-lg bg-[#050b0a] p-1">{(["5m", "15m", "30m", "1h", "4h", "1D", "1W", "1M"] as Interval[]).map((item) => <button key={item} onClick={() => setInterval(item)} className={`rounded-md px-3 py-1.5 text-xs font-bold ${interval === item ? "bg-[#50f2a7] text-[#04110b]" : "text-[#8da49a]"}`}>{item}</button>)}</div>
        {timeframe && <button onClick={() => setRegularSessionOnly((current) => !current)} className="rounded-md border border-[#29473e] px-2 py-1 text-[10px] font-bold text-[#9eb3aa]">{regularSessionOnly ? "RTH" : "Extended"}</button>}
        {timeframe && <button onClick={() => void loadIntraday(timeframe, true)} disabled={refreshing} className="rounded-md border border-[#29473e] px-2 py-1 text-[10px] font-bold text-[#9eb3aa]">{refreshing ? "Refreshing…" : "Refresh"}</button>}
        <button onClick={() => chartRef.current?.timeScale().fitContent()} className="rounded-md border border-[#29473e] px-2 py-1 text-[10px] font-bold text-[#9eb3aa]">Fit</button>
        <button onClick={exportChart} className="rounded-md border border-[#29473e] px-2 py-1 text-[10px] font-bold text-[#9eb3aa]">Export PNG</button>
        <button onClick={onToggleTradeCases} className="grid h-8 w-8 place-items-center rounded-md border border-[#29473e] text-[#9eb3aa] hover:border-[#50f2a7] hover:text-[#50f2a7]" title={tradeCasesOpen ? "Hide trade cases" : "Show trade cases"} aria-label={tradeCasesOpen ? "Hide trade cases" : "Show trade cases"}><PanelIcon open={tradeCasesOpen}/></button>
        <button onClick={onToggleExpanded} className="grid h-8 w-8 place-items-center rounded-md border border-[#29473e] text-[#9eb3aa] hover:border-[#50f2a7] hover:text-[#50f2a7]" title={expanded ? "Restore chart" : "Maximize chart"} aria-label={expanded ? "Restore chart" : "Maximize chart"}><ExpandIcon expanded={expanded}/></button>
      </div>
    </div>
    {legend && <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-b border-[#13231e] px-4 py-1.5 text-[10px] tabular-nums text-[#789087]"><span className="text-[#9eb3aa]">{legend.time}</span><span>O <b className="text-white">{legend.open.toFixed(2)}</b></span><span>H <b className="text-[#39dfa0]">{legend.high.toFixed(2)}</b></span><span>L <b className="text-[#fb7185]">{legend.low.toFixed(2)}</b></span><span>C <b className="text-white">{legend.close.toFixed(2)}</b></span><span>Vol <b className="text-white">{legend.volume.toLocaleString()}</b></span><span className={legend.close >= legend.open ? "text-[#39dfa0]" : "text-[#fb7185]"}>{legend.open ? `${(((legend.close - legend.open) / legend.open) * 100).toFixed(2)}%` : "—"}</span></div>}
    {patternOverlays.length > 0 && <div className="flex flex-wrap items-center gap-2 border-b border-[#1c312b] px-5 py-3">
      <span className="mr-1 text-[10px] font-black uppercase tracking-[.16em] text-[#60756d]">Pattern overlays</span>
      <button onClick={() => setSelectedPatterns(selectedPatterns.length === patternOverlays.length ? [] : patternOverlays.map((pattern) => pattern.id))} className="rounded-full border border-[#29473e] px-3 py-1 text-[11px] font-bold text-[#9eb3aa]">{selectedPatterns.length === patternOverlays.length ? "Hide all" : "Show all"}</button>
      <button onClick={() => setShowPatternLabels((current) => !current)} className={`rounded-full border px-3 py-1 text-[11px] font-bold ${showPatternLabels ? "border-[#50f2a7] text-[#50f2a7]" : "border-[#29473e] text-[#9eb3aa]"}`}>{showPatternLabels ? "Hide chart labels" : "Show chart labels"}</button>
      {patternOverlays.map((pattern) => <button key={pattern.id} onClick={() => togglePattern(pattern.id)} className={`rounded-full border px-3 py-1 text-[11px] font-bold transition ${selectedPatterns.includes(pattern.id) ? "text-[#04110b]" : "border-[#29473e] text-[#789087]"}`} style={selectedPatterns.includes(pattern.id) ? { backgroundColor: pattern.color, borderColor: pattern.color } : undefined}>{pattern.label}</button>)}
    </div>}
    {visibleData.length > 0 && !loading && <div className="flex items-center justify-between border-b border-[#13231e] px-4 py-1.5 text-[10px] text-[#60756d]"><span>Scroll to zoom · drag to pan · drag an axis to scale · double-click an axis to reset</span><div className="flex items-center gap-1"><span className="mr-1 uppercase tracking-wider">Price scale</span><select aria-label="Price scale mode" value={scaleMode} onChange={(event) => setScaleMode(event.target.value as ScaleMode)} className="rounded border border-[#29473e] bg-[#050b0a] px-1.5 py-1 text-[#9eb3aa]"><option value="normal">Linear</option><option value="log">Log</option><option value="percent">Percent</option><option value="indexed">Indexed 100</option></select><button onClick={() => zoomPriceScale(1.25)} className="rounded border border-[#29473e] px-2 py-1 text-[#9eb3aa]" title="Expand price range">−</button><button onClick={() => priceScaleRef.current?.setAutoScale(true)} className="rounded border border-[#29473e] px-2 py-1 text-[#9eb3aa]">Auto</button><button onClick={() => zoomPriceScale(.8)} className="rounded border border-[#29473e] px-2 py-1 text-[#9eb3aa]" title="Compress price range">+</button></div></div>}
    {loading ? <div className="grid h-[560px] place-items-center text-sm text-[#789087]">Loading {interval} candles…</div> : visibleData.length ? <div className={`relative w-full ${expanded ? "h-[calc(100vh-205px)] min-h-[640px]" : "h-[560px]"}`}>
      <div ref={ref} className="h-full w-full cursor-crosshair" />
      <div className="absolute left-2 top-2 z-30 flex w-9 flex-col items-center gap-0.5 rounded-lg border border-[#29473e] bg-[#07100ef2] p-1 shadow-xl shadow-black/40">
        {(["trend", "horizontal", "path", "fib", "brush", "text", "emoji"] as DrawingTool[]).map((tool) => <button key={tool} onClick={() => setTool(tool)} title={tool === "fib" ? "Fibonacci retracement" : tool[0].toUpperCase() + tool.slice(1)} aria-label={tool} className={`grid h-7 w-7 place-items-center rounded ${drawingTool === tool ? "bg-[#50f2a7] text-[#04110b]" : "text-[#c1d0ca] hover:bg-[#16352b]"}`}><span className="h-5 w-5"><DrawingIcon name={tool}/></span></button>)}
        <div className="my-1 h-px w-6 bg-[#29473e]"/>
        <button onClick={() => setTool("ruler")} title="Measure price change" aria-label="Measure price change" className={`grid h-7 w-7 place-items-center rounded ${drawingTool === "ruler" ? "bg-[#50f2a7] text-[#04110b]" : "text-[#c1d0ca] hover:bg-[#16352b]"}`}><span className="h-5 w-5"><DrawingIcon name="ruler"/></span></button>
        <button onClick={() => { const current = chartRef.current?.timeScale().getVisibleLogicalRange(); if (current) { const inset = (current.to - current.from) * .1; chartRef.current?.timeScale().setVisibleLogicalRange({ from: current.from + inset, to: current.to - inset }); } }} title="Zoom in" aria-label="Zoom in" className="grid h-7 w-7 place-items-center rounded text-[#c1d0ca] hover:bg-[#16352b]"><span className="h-5 w-5"><DrawingIcon name="zoom"/></span></button>
        <div className="my-1 h-px w-6 bg-[#29473e]"/>
        <button onClick={() => setMagnetEnabled((current) => !current)} title="Snap drawings to OHLC" aria-label="Snap drawings to OHLC" className={`grid h-7 w-7 place-items-center rounded ${magnetEnabled ? "bg-[#16352b] text-[#50f2a7]" : "text-[#c1d0ca] hover:bg-[#16352b]"}`}><span className="h-5 w-5"><DrawingIcon name="magnet"/></span></button>
        <button onClick={() => { setDrawingsLocked((current) => !current); setDrawingTool("cursor"); setDraftPoints([]); }} title={drawingsLocked ? "Unlock drawings" : "Lock drawings"} aria-label={drawingsLocked ? "Unlock drawings" : "Lock drawings"} className={`grid h-7 w-7 place-items-center rounded ${drawingsLocked ? "bg-[#16352b] text-[#50f2a7]" : "text-[#c1d0ca] hover:bg-[#16352b]"}`}><span className="h-5 w-5"><DrawingIcon name="lock"/></span></button>
        <button onClick={() => setDrawingsVisible((current) => !current)} title={drawingsVisible ? "Hide drawings" : "Show drawings"} aria-label={drawingsVisible ? "Hide drawings" : "Show drawings"} className={`grid h-7 w-7 place-items-center rounded ${!drawingsVisible ? "bg-[#16352b] text-[#50f2a7]" : "text-[#c1d0ca] hover:bg-[#16352b]"}`}><span className="h-5 w-5"><DrawingIcon name="eye"/></span></button>
        <div className="my-1 h-px w-6 bg-[#29473e]"/>
        <button onClick={() => { setDrawingsByInterval((current) => ({ ...current, [interval]: [] })); setDraftPoints([]); }} title="Clear drawings" aria-label="Clear drawings" className="grid h-7 w-7 place-items-center rounded text-[#fb7185] hover:bg-[#3b1720]"><span className="h-5 w-5"><DrawingIcon name="trash"/></span></button>
      </div>
      <svg className="absolute inset-0 z-20 h-full w-full" style={{ pointerEvents: drawingTool === "cursor" || drawingsLocked ? "none" : "auto", cursor: drawingTool === "text" ? "text" : "crosshair" }} onClick={drawingClick} onDoubleClick={finishPath} onPointerDown={drawingPointerDown} onPointerMove={drawingPointerMove} onPointerUp={drawingPointerUp} onPointerLeave={() => setPreviewPoint(null)}>
        {drawingsVisible && drawings.map(drawingShape)}
        {drawingsVisible && draftPoints.length > 0 && <polyline points={[...draftPoints, ...(previewPoint && drawingTool !== "brush" ? [previewPoint] : [])].map(pixelPoint).filter(Boolean).map((point: any) => `${point.x},${point.y}`).join(" ")} fill="none" stroke="#50f2a7" strokeWidth="2" strokeDasharray={drawingTool === "brush" ? undefined : "5 4"}/>} 
      </svg>
    </div> : <div className="grid h-[560px] place-items-center px-6 text-center"><div><p className="font-bold text-white">No {interval} prices available</p><p className="mt-2 max-w-md text-sm text-[#789087]">{error || "No prices are available for this date range."}</p></div></div>}
    {data.length > 0 && !loading && <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[#1c312b] px-4 py-2"><div className="flex flex-wrap items-center gap-1">{rangeOptions.map((item) => <button key={item} onClick={() => { setRange(item); setShowCustomRange(false); }} className={`rounded px-2.5 py-1 text-[11px] font-bold ${range === item ? "bg-[#16352b] text-[#50f2a7]" : "text-[#789087] hover:text-white"}`}>{item}</button>)}</div><div className="flex flex-wrap items-center justify-end gap-2">{showCustomRange && <><input aria-label="Start date" type="date" value={customStart} onChange={(event) => { setCustomStart(event.target.value); setRange("CUSTOM"); }} className="rounded border border-[#29473e] bg-[#050b0a] px-2 py-1 text-[11px] text-[#9eb3aa]"/><span className="text-xs text-[#60756d]">to</span><input aria-label="End date" type="date" value={customEnd} onChange={(event) => { setCustomEnd(event.target.value); setRange("CUSTOM"); }} className="rounded border border-[#29473e] bg-[#050b0a] px-2 py-1 text-[11px] text-[#9eb3aa]"/></>}<button onClick={() => setShowCustomRange((current) => !current)} className={`rounded-lg border px-3 py-1.5 text-[11px] font-bold ${range === "CUSTOM" ? "border-[#50f2a7] text-[#50f2a7]" : "border-[#29473e] text-[#9eb3aa]"}`}>Date range</button></div></div>}
  </div>;
}
