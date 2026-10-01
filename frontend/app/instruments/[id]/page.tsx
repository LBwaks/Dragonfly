import { redirect } from "next/navigation";
import InstrumentWorkspace from "../../../components/InstrumentWorkspace";

const api = process.env.API_URL ?? "http://localhost:8000";
async function read(path: string) { return fetch(api + path, { cache: "no-store" }).then((response) => response.ok ? response.json() : null).catch(() => null); }
function rows(value: any) { return Array.isArray(value) ? value : value?.results ?? []; }
function metric(value: any, suffix = "") { return value === null || value === undefined ? "—" : `${Number(value).toFixed(2)}${suffix}`; }

export default async function Instrument({ params }: { params: Promise<{ id: string }> }) {
  const { id: locator } = await params;
  const numericLocator = /^\d+$/.test(locator);
  const lookup = numericLocator ? await read(`/api/v1/instruments/${locator}/`) : rows(await read(`/api/v1/instruments/?symbol=${encodeURIComponent(locator)}`))[0];
  if (!lookup?.id) return <div className="rounded-xl border border-rose-400/20 bg-rose-400/5 p-6">Instrument not found.</div>;
  if (numericLocator) redirect(`/instruments/${lookup.symbol.toLowerCase()}`);
  const instrument = lookup;
  const [pricesData, technicalData, signalData, fundamentalData, profileData, livePrice] = await Promise.all([
    read(`/api/v1/instruments/${instrument.id}/prices/`), read(`/api/v1/instruments/${instrument.id}/technicals/`),
    read(`/api/v1/instruments/${instrument.id}/signals/`), read(`/api/v1/instruments/${instrument.id}/fundamentals/`),
    read(`/api/v1/instruments/${instrument.id}/profile/`), read(`/api/v1/instruments/${instrument.id}/live-price/`),
  ]);
  const prices = rows(pricesData); const technicals = rows(technicalData); const signals = rows(signalData);
  const patterns = Array.from(new Set(signals.flatMap((signal: any) => [...(signal.candle_patterns ?? []), ...(signal.chart_patterns ?? [])]))) as string[];
  const technical = technicals[0] ?? {}; const fundamental = rows(fundamentalData)[0] ?? {}; const profile = rows(profileData)[0] ?? {};
  const displayedPrice = livePrice?.price ?? instrument.latest_price ?? prices[0]?.close;
  const priceProvider = livePrice ? `${livePrice.provider}${livePrice.feed ? ` · ${livePrice.feed.toUpperCase()}` : ""}` : instrument.price_provider || prices[0]?.provider || "No price provider data";
  return <div className="space-y-4">
    <header className="flex flex-col gap-3 border-b border-[#1c312b] pb-3 lg:flex-row lg:items-center lg:justify-between">
      <div className="min-w-0"><div className="flex items-center gap-2"><span className="rounded bg-[#16352b] px-2 py-0.5 text-[10px] font-black text-[#50f2a7]">{instrument.exchange}</span><span className="text-xs text-[#789087]">{instrument.sector || "Unclassified"}</span></div><div className="mt-1.5 flex flex-wrap items-baseline gap-x-3"><h1 className="text-4xl font-black tracking-[-.05em]">{instrument.symbol}</h1><p className="truncate text-sm text-[#9eb3aa]">{instrument.name}</p></div></div>
      <div className="lg:text-right"><div className="flex items-baseline gap-2 lg:justify-end"><span className="text-[10px] uppercase tracking-wider text-[#789087]">Latest</span><p className="text-3xl font-black tabular-nums">{displayedPrice ? `$${Number(displayedPrice).toFixed(2)}` : "—"}</p></div><p className="text-[10px] text-[#60756d]">{priceProvider}{livePrice?.as_of ? ` · ${new Date(livePrice.as_of).toLocaleString("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })} ET` : ""}</p>{patterns.length > 0 && <div className="mt-1.5 flex max-w-2xl flex-wrap gap-1 lg:justify-end">{patterns.map((pattern) => <span key={pattern} className="rounded-full border border-[#1d5f49] bg-[#0d2a21] px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide text-[#50f2a7]">{pattern.replaceAll("_", " ")}</span>)}</div>}</div>
    </header>
    <InstrumentWorkspace bars={prices} instrumentId={instrument.id} apiBase={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} signals={signals} />
    <section><h2 className="mb-3 text-xl font-black">Technical snapshot</h2><div className="grid gap-px overflow-hidden rounded-xl border border-[#1c312b] bg-[#1c312b] sm:grid-cols-2 lg:grid-cols-4">{[["RSI (14)",metric(technical.rsi_14)],["SMA 20",metric(technical.sma_20)],["SMA 50",metric(technical.sma_50)],["SMA 200",metric(technical.sma_200)],["MACD",metric(technical.macd)],["ATR %",metric(technical.atr_pct,"%")],["Relative volume",metric(technical.relative_volume)],["20D return",metric(technical.return_20d ? technical.return_20d * 100 : null,"%")]].map(([label,value]) => <div key={label} className="bg-[#091210] p-4"><p className="text-[10px] uppercase tracking-wider text-[#789087]">{label}</p><p className="mt-1 text-lg font-black tabular-nums">{value}</p></div>)}</div></section>
    <section><h2 className="mb-3 text-xl font-black">Fundamentals & company</h2><div className="grid gap-px overflow-hidden rounded-xl border border-[#1c312b] bg-[#1c312b] sm:grid-cols-2 lg:grid-cols-4">{[["Market cap",profile.market_cap ? `$${Number(profile.market_cap).toLocaleString()}M` : instrument.market_cap ? `$${Number(instrument.market_cap).toLocaleString()}` : "—"],["P/E",metric(fundamental.pe)],["EPS growth",metric(fundamental.eps_growth ? fundamental.eps_growth*100 : null,"%")],["Revenue growth",metric(fundamental.revenue_growth ? fundamental.revenue_growth*100 : null,"%")],["ROE",metric(fundamental.roe ? fundamental.roe*100 : null,"%")],["Debt / Equity",metric(fundamental.debt_equity)],["Industry",instrument.industry || "—"],["Currency",instrument.currency]].map(([label,value]) => <div key={label} className="bg-[#091210] p-4"><p className="text-[10px] uppercase tracking-wider text-[#789087]">{label}</p><p className="mt-1 truncate text-base font-black">{value}</p></div>)}</div></section>
  </div>;
}
