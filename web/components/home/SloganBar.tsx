import Link from "next/link";
import { SITE } from "@/lib/constants";

export function SloganBar() {
  return (
    <section className="py-12 flex flex-col items-center gap-4 text-center">
      <div className="w-16 h-px bg-earth-gold/40" />
      <p className="text-lg font-serif text-earth-100 tracking-wide">
        {SITE.mission}
      </p>
      <Link
        href="/archive"
        className="mt-4 text-xs tracking-widest uppercase text-earth-blue hover:text-earth-100 transition-colors"
      >
        View Archive &rarr;
      </Link>
    </section>
  );
}
