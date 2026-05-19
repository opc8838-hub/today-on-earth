import { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { getArchiveSummary } from "@/lib/database";
import type { DaySummary } from "@/types";

export const metadata: Metadata = {
  title: "Archive",
};

export const revalidate = 3600;

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default async function ArchivePage() {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;

  // Fetch current month's data
  const days = await getArchiveSummary(currentYear, currentMonth);

  // Build calendar grid
  const firstDay = new Date(currentYear, currentMonth - 1, 1);
  const lastDay = new Date(currentYear, currentMonth, 0);
  const startDayOfWeek = firstDay.getDay(); // 0=Sun
  const totalDays = lastDay.getDate();

  // Build a map for quick lookup
  const dayMap: Record<string, DaySummary> = {};
  for (const d of days) {
    dayMap[d.date] = d;
  }

  // Generate calendar cells
  const cells: (DaySummary | null)[] = [];
  // Leading blanks
  for (let i = 0; i < startDayOfWeek; i++) {
    cells.push(null);
  }
  // Actual days
  for (let d = 1; d <= totalDays; d++) {
    const dateStr = `${currentYear}-${String(currentMonth).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push(dayMap[dateStr] ?? null);
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="text-center mb-12">
        <p className="text-[10px] tracking-[.3em] uppercase text-earth-blue mb-4">
          Archive &middot; 历史回看
        </p>
        <h1 className="text-2xl font-serif font-bold text-earth-100">
          {MONTH_NAMES[currentMonth - 1]} {currentYear}
        </h1>
      </div>

      {days.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <p className="text-earth-500 text-sm">
            No videos archived yet for this month.
          </p>
          <p className="text-earth-600 text-xs mt-2">
            Videos will appear here once they are published.
          </p>
        </div>
      )}

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-px bg-earth-700 rounded-lg overflow-hidden">
        {/* Day headers */}
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div
            key={day}
            className="bg-earth-800 px-2 py-2 text-center text-[10px] tracking-widest uppercase text-earth-500"
          >
            {day}
          </div>
        ))}

        {/* Day cells */}
        {cells.map((cell, i) => {
          const dayNum = i - startDayOfWeek + 1;
          const isToday =
            cell?.date === now.toISOString().split("T")[0];

          return (
            <div
              key={i}
              className={`bg-earth-900 min-h-[80px] p-2 ${
                cell ? "hover:bg-earth-800 transition-colors" : ""
              }`}
            >
              {cell ? (
                <Link
                  href={`/day/${cell.date}`}
                  className="block h-full"
                >
                  <span
                    className={`text-xs font-mono ${
                      isToday
                        ? "text-earth-blue font-bold"
                        : "text-earth-300"
                    }`}
                  >
                    {dayNum}
                  </span>
                  {/* Cover thumbnail placeholder */}
                  {cell.cover_url && (
                    <div className="mt-1 aspect-video rounded-sm bg-earth-800 overflow-hidden relative">
                      <Image
                        src={cell.cover_url}
                        alt=""
                        fill
                        className="object-cover opacity-60 hover:opacity-100 transition-opacity"
                        unoptimized
                      />
                    </div>
                  )}
                  {/* Location hints */}
                  {cell.cities.length > 0 && (
                    <p className="mt-1 text-[9px] text-earth-500 truncate leading-tight">
                      {cell.cities.slice(0, 2).join(", ")}
                      {cell.cities.length > 2 && "…"}
                    </p>
                  )}
                  {/* Slot indicators */}
                  <div className="flex gap-1 mt-1">
                    {cell.has_morning && (
                      <span className="w-1.5 h-1.5 rounded-full bg-earth-gold" />
                    )}
                    {cell.has_afternoon && (
                      <span className="w-1.5 h-1.5 rounded-full bg-earth-blue" />
                    )}
                  </div>
                </Link>
              ) : (
                <span className="text-xs text-earth-800">{dayNum || ""}</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-6">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-earth-gold" />
          <span className="text-[10px] text-earth-500">Morning</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-earth-blue" />
          <span className="text-[10px] text-earth-500">Afternoon</span>
        </div>
      </div>
    </div>
  );
}
