import ScoreBadge from "./ScoreBadge";

export default function SignalTable({ signals, compact = false }: { signals: any[]; compact?: boolean }) {
  if (!signals?.length) return <div className="rounded-2xl border border-dashed border-[#29473e] p-8 text-center text-[#81978e]">No scored opportunities yet. Ingest prices and generate trade signals.</div>;
  return <div className="overflow-hidden rounded-2xl border border-[#1c312b] bg-[#091210]">
    <div className="overflow-x-auto"><table className="w-full text-left text-sm">
      <thead className="border-b border-[#1c312b] text-[11px] uppercase tracking-[.16em] text-[#789087]"><tr>
        <th className="px-5 py-4">Stock</th><th className="px-5 py-4">Case</th><th className="px-5 py-4">Horizon</th>
        <th className="px-5 py-4">Price</th><th className="px-5 py-4">Score</th>{!compact && <><th className="px-5 py-4">Technical</th><th className="px-5 py-4">Pattern</th></>}
      </tr></thead>
      <tbody>{signals.map((signal) => <tr key={signal.id} className="border-b border-[#152620] transition hover:bg-[#10201b]">
        <td className="px-5 py-4"><a className="font-black text-white hover:text-[#50f2a7]" href={`/instruments/${signal.symbol.toLowerCase()}`}>{signal.symbol}</a><div className="mt-1 max-w-52 truncate text-xs text-[#789087]">{signal.name}</div></td>
        <td className={`px-5 py-4 font-bold ${signal.case_type === "BULL" ? "text-emerald-400" : "text-rose-400"}`}>{signal.case_type}</td>
        <td className="px-5 py-4 text-[#a7bbb3]">{signal.horizon}</td><td className="px-5 py-4 tabular-nums">${Number(signal.price).toFixed(2)}</td>
        <td className="px-5 py-4"><ScoreBadge score={signal.score} side={signal.case_type} /></td>
        {!compact && <><td className="px-5 py-4 tabular-nums">{Number(signal.technical_score).toFixed(0)}</td><td className="px-5 py-4 tabular-nums">{Number(signal.pattern_score).toFixed(0)}</td></>}
      </tr>)}</tbody>
    </table></div>
  </div>;
}
