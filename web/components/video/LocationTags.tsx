import { Badge } from "@/components/ui/Badge";

interface LocationTagsProps {
  countries: string[];
  cities: string[];
  className?: string;
}

export function LocationTags({
  countries,
  cities,
  className = "",
}: LocationTagsProps) {
  if (countries.length === 0 && cities.length === 0) return null;

  return (
    <div className={`flex flex-wrap gap-1.5 ${className}`}>
      {cities.map((city, i) => (
        <Badge key={`city-${i}`} variant="gold">
          {city}
        </Badge>
      ))}
      {countries.map((country, i) => (
        <Badge key={`country-${i}`}>{country}</Badge>
      ))}
    </div>
  );
}
