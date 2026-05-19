import type { DailyVideo } from "@/types";
import { Badge } from "@/components/ui/Badge";

interface LocationListProps {
  videos: DailyVideo[];
  className?: string;
}

export function LocationList({ videos, className = "" }: LocationListProps) {
  // Collect unique locations from all videos today
  const allCities: string[] = [];
  const allCountries: string[] = [];

  for (const v of videos) {
    if (v.cities) {
      for (const c of v.cities) {
        if (!allCities.includes(c)) allCities.push(c);
      }
    }
    if (v.countries) {
      for (const c of v.countries) {
        if (!allCountries.includes(c)) allCountries.push(c);
      }
    }
  }

  if (allCities.length === 0) return null;

  return (
    <section className={`py-12 ${className}`}>
      <p className="text-[10px] tracking-[.3em] uppercase text-earth-blue mb-4">
        Today&apos;s Locations &middot; 今日位置
      </p>
      <div className="flex flex-wrap gap-2">
        {allCities.map((city, i) => (
          <Badge key={i} variant="gold">
            {city}
            {allCountries[i] && (
              <span className="text-earth-500 ml-1.5">{allCountries[i]}</span>
            )}
          </Badge>
        ))}
      </div>
    </section>
  );
}
