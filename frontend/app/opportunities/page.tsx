import SignalTable from "../../components/SignalTable";

const api = process.env.API_URL ?? "http://localhost:8000";
type Props = { searchParams: Promise<{ case?: string; horizon?: string; page?: string }> };

export default async function Opportunities({ searchParams }: Props) {
  const params = await searchParams;
  const side = params.case === "BEAR" ? "BEAR" : "BULL";
  const horizon = ["DAILY", "WEEKLY", "MONTHLY"].includes(params.horizon ?? "") ? params.horizon! : "DAILY";
  const page = Math.max(1, Number(params.page ?? 1));
  const data = await fetch(`${api}/api/v1/trade-signals/?case_type=${side}&horizon=${horizon}&page=${page}`, { cache: "no-store" }).then((r) => r.json()).catch(() => ({ results: [], count: 0 }));
  return <div className="space-y-7">
    <header><p className="text-xs font-black tracking-[.22em] text-[#50f2a7]">OPPORTUNITY ENGINE</p><h1 className="mt-3 text-5xl font-black tracking-[-.04em]">Bull & Bear cases</h1><p className="mt-3 max-w-2xl text-[#8da49a]">Ranked, explainable setups across daily, weekly, and monthly trading horizons.</p></header>
    <div className="flex flex-wrap gap-3">
      {(["BULL", "BEAR"] as const).map((item) => <a key={item} href={`/opportunities?case=${item}&horizon=${horizon}`} className={`rounded-lg px-5 py-2.5 text-sm font-black ${side === item ? (item === "BULL" ? "bg-emerald-400 text-emerald-950" : "bg-rose-400 text-rose-950") : "border border-[#29473e] text-[#91a79e]"}`}>{item} CASE</a>)}
      <span className="mx-1 hidden w-px bg-[#29473e] sm:block" />
      {["DAILY", "WEEKLY", "MONTHLY"].map((item) => <a key={item} href={`/opportunities?case=${side}&horizon=${item}`} className={`rounded-lg px-4 py-2.5 text-sm font-bold ${horizon === item ? "bg-white text-black" : "border border-[#29473e] text-[#91a79e]"}`}>{item}</a>)}
    </div>
    <SignalTable signals={data.results ?? []} />
    <div className="flex items-center justify-between text-sm text-[#8da49a]">{data.previous ? <a className="text-[#50f2a7]" href={`/opportunities?case=${side}&horizon=${horizon}&page=${page - 1}`}>← Previous</a> : <span/>}<span>{data.count ?? 0} opportunities</span>{data.next ? <a className="text-[#50f2a7]" href={`/opportunities?case=${side}&horizon=${horizon}&page=${page + 1}`}>Next →</a> : <span/>}</div>
  </div>;
}
