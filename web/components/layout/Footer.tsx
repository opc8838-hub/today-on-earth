import { SITE } from "@/lib/constants";

export default function Footer() {
  return (
    <footer className="border-t border-earth-700">
      <div className="max-w-8xl mx-auto px-6 py-8 flex flex-col items-center gap-3">
        <p className="text-xs text-earth-300 tracking-wider">
          {SITE.name} &middot; {SITE.nameCN}
        </p>
        <p className="text-[10px] text-earth-600 tracking-widest uppercase">
          Inspired by earthTV&reg;
        </p>
        <p className="text-[10px] text-earth-600">
          &copy; {new Date().getFullYear()} {SITE.name}. All footage from public sources.
        </p>
      </div>
    </footer>
  );
}
