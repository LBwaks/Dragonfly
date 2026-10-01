import SignalTable from "../components/SignalTable";

const api = process.env.API_URL ?? "http://localhost:8000";
async function read(path: string) { return fetch(api + path, { cache: "no-store" }).then((r) => r.json()).catch(() => ({ results: [], count: 0 })); }

export default async function Dashboard() {
  const [bulls, bears, instruments] = await Promise.all([
    read("/api/v1/trade-signals/?case_type=BULL&horizon=DAILY"),
    read("/api/v1/trade-signals/?case_type=BEAR&horizon=DAILY"),
    read("/api/v1/instruments/"),
  ]);
  const bullRows = bulls.results ?? [];
  const bearRows = bears.results ?? [];
  return <div className="space-y-10">
    <section className="grid gap-6 border-b border-[#1c312b] pb-10 lg:grid-cols-[1fr_auto] lg:items-end">
      <div><p className="text-xs font-black tracking-[.25em] text-[#50f2a7]">TRADE INTELLIGENCE</p>
        <h1 className="mt-4 max-w-4xl text-5xl font-black tracking-[-.05em] text-white md:text-7xl">Find the setup.<br/><span className="text-[#789087]">Measure the evidence.</span></h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-[#9eb3aa]">Technical trend, fundamentals, macro context, price action, and candlestick patterns—combined into explainable Bull and Bear cases.</p>
      </div>
      <a href="/opportunities" className="rounded-xl bg-[#50f2a7] px-6 py-3 text-center text-sm font-black text-[#04110b]">Explore opportunities →</a>
    </section>

    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {[
        [instruments.count ?? 0, "Active instruments", "Provider universe"],
        [bulls.count ?? 0, "Daily bull cases", "Ranked high to low"],
        [bears.count ?? 0, "Daily bear cases", "Ranked high to low"],
        [bullRows[0]?.as_of_date ?? "—", "Latest analysis", "Completed market date"],
      ].map(([value, label, note]) => <article key={String(label)} className="rounded-2xl border border-[#1c312b] bg-[#091210] p-5"><p className="text-3xl font-black tabular-nums text-white">{value}</p><p className="mt-2 font-semibold">{label}</p><p className="mt-1 text-xs text-[#789087]">{note}</p></article>)}
    </section>

    <section className="grid gap-8 xl:grid-cols-2">
      <div><div className="mb-4 flex items-center justify-between"><div><p className="text-xs font-black tracking-[.2em] text-emerald-400">BULL CASE</p><h2 className="mt-1 text-2xl font-black">Daily leaders</h2></div><a href="/opportunities?case=BULL&horizon=DAILY" className="text-sm text-[#50f2a7]">View all</a></div><SignalTable signals={bullRows.slice(0, 5)} compact /></div>
      <div><div className="mb-4 flex items-center justify-between"><div><p className="text-xs font-black tracking-[.2em] text-rose-400">BEAR CASE</p><h2 className="mt-1 text-2xl font-black">Daily weakness</h2></div><a href="/opportunities?case=BEAR&horizon=DAILY" className="text-sm text-[#50f2a7]">View all</a></div><SignalTable signals={bearRows.slice(0, 5)} compact /></div>
    </section>
    <p className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-4 text-xs leading-5 text-amber-100/70">Scores measure setup quality from available evidence. They are not guaranteed profitability percentages or financial advice. Backtested calibration is required before interpreting a score as win probability.</p>
  </div>;
}
