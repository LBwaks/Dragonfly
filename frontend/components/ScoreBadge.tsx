export default function ScoreBadge({ score, side }: { score: number; side: "BULL" | "BEAR" }) {
  const tone = side === "BULL" ? "text-emerald-300 border-emerald-400/30 bg-emerald-400/10" : "text-rose-300 border-rose-400/30 bg-rose-400/10";
  return <span className={`inline-flex min-w-16 justify-center rounded-full border px-3 py-1 text-sm font-black tabular-nums ${tone}`}>{Number(score).toFixed(0)}</span>;
}
