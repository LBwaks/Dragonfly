import "./styles.css";

export const metadata = {
  title: "Dragonfly · Trade Intelligence",
  description: "Technical, fundamental, macro, and price-action trade discovery",
};

const links = [
  ["Dashboard", "/"],
  ["Opportunities", "/opportunities"],
  ["Macro", "/macro"],
  ["Instruments", "/instruments"],
  ["Screeners", "/screeners"],
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>
    <header className="sticky top-0 z-50 border-b border-[#1c312b] bg-[#050b0a]/90 backdrop-blur-xl">
      <div className="flex h-12 w-full items-center justify-between px-3 lg:px-4">
        <a href="/" className="flex items-center gap-3 font-black tracking-tight">
          <span className="grid size-7 place-items-center rounded-lg bg-[#50f2a7] text-sm text-[#04110b]">D</span>
          <span>DRAGONFLY</span>
        </a>
        <nav className="hidden items-center gap-7 text-sm text-[#9eb3aa] md:flex">
          {links.map(([label, href]) => <a key={href} className="transition hover:text-white" href={href}>{label}</a>)}
        </nav>
        <a href="/login" className="rounded-lg border border-[#29473e] px-3 py-1.5 text-xs font-semibold hover:border-[#50f2a7]">Sign in</a>
      </div>
    </header>
    <main className="w-full px-3 py-4 lg:px-4 lg:py-5">{children}</main>
  </body></html>;
}
