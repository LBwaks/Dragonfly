const api = process.env.API_URL ?? "http://localhost:8000";

export default async function Screeners() {
  const data = await fetch(api + "/api/v1/screeners/", { cache: "no-store" }).then((r) => r.json()).catch(() => ({ results: [] }));
  return <div className="space-y-8"><header><p className="text-xs font-black tracking-[.22em] text-[#50f2a7]">CUSTOM DISCOVERY</p><h1 className="mt-3 text-5xl font-black tracking-[-.04em]">Screeners</h1><p className="mt-3 max-w-2xl text-[#8da49a]">Saved rule sets combine technical, fundamental, analyst, insider, and event evidence.</p></header>
    {data.results?.length ? <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{data.results.map((screener: any) => <article key={screener.id} className="rounded-2xl border border-[#1c312b] bg-[#091210] p-6"><span className="text-xs font-black tracking-widest text-[#50f2a7]">{screener.is_builtin ? "BUILT IN" : "CUSTOM"}</span><h2 className="mt-3 text-xl font-black">{screener.name}</h2><p className="mt-2 text-sm leading-6 text-[#8da49a]">{screener.description}</p></article>)}</div> : <div className="rounded-2xl border border-dashed border-[#29473e] p-10 text-center text-[#8da49a]">Sign in to create and run custom screeners.</div>}
  </div>;
}
