"use client";

import { Globe } from "lucide-react";

export function EarthSignal({ active = true }: { active?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <Globe
          className={`w-4 h-4 ${active ? "text-earth-blue" : "text-earth-600"}`}
        />
        {active && (
          <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-earth-blue animate-pulse" />
        )}
      </div>
      {active && (
        <span className="text-[10px] tracking-widest uppercase text-earth-blue">
          LIVE
        </span>
      )}
    </div>
  );
}
