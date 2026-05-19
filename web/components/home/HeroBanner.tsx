import { SITE } from "@/lib/constants";

export function HeroBanner() {
  const today = new Date();
  const dateStr = today.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });

  return (
    <section className="text-center py-16 sm:py-20">
      <p className="text-[10px] tracking-[.3em] uppercase text-earth-blue mb-4">
        {SITE.nameCN} &middot; {SITE.name}
      </p>
      <h1 className="text-2xl sm:text-3xl font-serif font-bold text-earth-100 mb-3 tracking-wide">
        {SITE.slogan}
      </h1>
      <p className="text-sm text-earth-600 font-mono tracking-wider">
        {dateStr}
      </p>
    </section>
  );
}
