"use client";

import { useState } from "react";
import PriceChart from "./PriceChart";
import ScoreBadge from "./ScoreBadge";

export default function InstrumentWorkspace({ bars, instrumentId, apiBase, signals }: { bars: any[]; instrumentId: number; apiBase: string; signals: any[] }) {
  const [tradeCasesOpen, setTradeCasesOpen] = useState(true);
  const [chartExpanded, setChartExpanded] = useState(false);
  const showCases = tradeCasesOpen && !chartExpanded;
  return <section className={`grid gap-3 ${showCases ? "xl:grid-cols-[minmax(0,1fr)_310px]" : "grid-cols-1"}`}>
    <PriceChart
      bars={bars}
      instrumentId={instrumentId}
      apiBase={apiBase}
      expanded={chartExpanded}
      onToggleExpanded={() => setChartExpanded((current) => !current)}
      tradeCasesOpen={showCases}
      onToggleTradeCases={() => setTradeCasesOpen((current) => !current)}
    />
    {showCases && <aside className="min-w-0 space-y-3">
      <div className="flex items-center justify-between px-1"><h2 className="text-lg font-black">Trade cases</h2><button onClick={() => setTradeCasesOpen(false)} className="rounded-lg border border-[#29473e] px-2.5 py-1.5 text-xs font-bold text-[#9eb3aa] hover:border-[#50f2a7]">Hide</button></div>
      {signals.length ? signals.map((signal: any) => <article key={signal.id} className={`rounded-xl border p-4 ${signal.case_type === "BULL" ? "border-emerald-400/25 bg-emerald-400/5" : "border-rose-400/25 bg-rose-400/5"}`}>
        <div className="flex items-center justify-between"><div><p className={`text-[10px] font-black tracking-[.18em] ${signal.case_type === "BULL" ? "text-emerald-400" : "text-rose-400"}`}>{signal.case_type} CASE</p><h3 className="mt-1 text-sm font-bold">{signal.horizon}</h3></div><ScoreBadge score={signal.score} side={signal.case_type}/></div>
        <ul className="mt-3 space-y-1.5 text-[11px] text-[#9eb3aa]">{signal.rationale?.slice(0, 4).map((item: string) => <li key={item}>• {item}</li>)}</ul>
      </article>) : <div className="rounded-xl border border-dashed border-[#29473e] p-5 text-sm text-[#789087]">No scored case yet. This stock needs sufficient historical bars and a completed signal run.</div>}
    </aside>}
  </section>;
}
