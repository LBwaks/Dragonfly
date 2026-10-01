const api = process.env.API_URL ?? "http://localhost:8000";
type PageProps = { searchParams: Promise<{ page?: string; symbol?: string }> };

export default async function Instruments({ searchParams }: PageProps) {
  const params = await searchParams;
  const page = Math.max(1, Number.parseInt(params.page ?? "1", 10) || 1);
  const symbol = (params.symbol ?? "").trim().toUpperCase();
  const query = symbol ? `symbol=${encodeURIComponent(symbol)}` : `page=${page}`;
  const data = await fetch(`${api}/api/v1/instruments/?${query}`, { cache: "no-store" }).then((r) => r.json()).catch(() => ({ count: 0, results: [] }));
  return <div className="space-y-7">
    <header className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
      <div><p className="text-xs font-black tracking-[.22em] text-[#50f2a7]">UNIVERSE · {data.count ?? 0} ASSETS</p><h1 className="mt-3 text-5xl font-black tracking-[-.04em]">Instruments</h1><p className="mt-3 text-[#8da49a]">Provider-normalized equities, prices, classifications, and market metadata.</p></div>
      <form className="flex gap-2" action="/instruments"><input name="symbol" defaultValue={symbol} placeholder="Find symbol, e.g. NVDA" className="w-64 rounded-xl border border-[#29473e] bg-[#091210] px-4 py-3 text-sm outline-none placeholder:text-[#5f756c] focus:border-[#50f2a7]"/><button className="rounded-xl bg-[#50f2a7] px-5 py-3 text-sm font-black text-[#04110b]">Search</button></form>
    </header>
    <div className="overflow-hidden rounded-2xl border border-[#1c312b] bg-[#091210]"><div className="overflow-x-auto"><table className="w-full min-w-[850px] text-left text-sm">
      <thead className="border-b border-[#1c312b] text-[11px] uppercase tracking-[.16em] text-[#789087]"><tr><th className="px-5 py-4">Symbol</th><th className="px-5 py-4">Name</th><th className="px-5 py-4">Sector</th><th className="px-5 py-4 text-right">Price</th><th className="px-5 py-4">Exchange</th></tr></thead>
      <tbody>{data.results?.map((instrument: any) => <tr key={instrument.id} className="border-b border-[#152620] transition hover:bg-[#10201b]"><td className="px-5 py-4"><a href={`/instruments/${instrument.symbol.toLowerCase()}`} className="font-black text-white hover:text-[#50f2a7]">{instrument.symbol}</a></td><td className="max-w-md truncate px-5 py-4">{instrument.name}</td><td className="px-5 py-4 text-[#9eb3aa]">{instrument.sector || "Unclassified"}</td><td className="px-5 py-4 text-right font-semibold tabular-nums">{instrument.latest_price ? `$${Number(instrument.latest_price).toFixed(2)}` : "—"}</td><td className="px-5 py-4 text-[#9eb3aa]">{instrument.exchange}</td></tr>)}</tbody>
    </table></div></div>
    {!symbol && <nav className="grid grid-cols-3 items-center text-sm text-[#8da49a]">{data.previous ? <a className="text-[#50f2a7]" href={`/instruments?page=${page - 1}`}>← Previous</a> : <span/>}<span className="text-center">Page {page} of {Math.max(1, Math.ceil((data.count ?? 0) / 50))}</span>{data.next ? <a className="text-right text-[#50f2a7]" href={`/instruments?page=${page + 1}`}>Next →</a> : <span/>}</nav>}
  </div>;
}
