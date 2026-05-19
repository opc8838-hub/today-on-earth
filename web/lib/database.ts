import { supabase } from "./supabase";
import type { DailyVideo, DaySummary } from "@/types";

/** Get today's videos (morning + afternoon) */
export async function getTodayVideos(): Promise<DailyVideo[]> {
  const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
  const { data, error } = await supabase
    .from("daily_videos")
    .select("*")
    .eq("date", today)
    .eq("is_published", true)
    .order("time_slot", { ascending: true });

  if (error) {
    console.error("getTodayVideos error:", error);
    return [];
  }
  return data as DailyVideo[];
}

/** Get videos for a specific date */
export async function getVideosByDate(
  date: string
): Promise<DailyVideo[]> {
  const { data, error } = await supabase
    .from("daily_videos")
    .select("*")
    .eq("date", date)
    .eq("is_published", true)
    .order("time_slot", { ascending: true });

  if (error) {
    console.error("getVideosByDate error:", error);
    return [];
  }
  return data as DailyVideo[];
}

/** Get archive summary: which days have videos */
export async function getArchiveSummary(
  year: number,
  month: number
): Promise<DaySummary[]> {
  const startDate = `${year}-${String(month).padStart(2, "0")}-01`;
  const endDate = `${year}-${String(month).padStart(2, "0")}-31`;

  const { data, error } = await supabase
    .from("daily_videos")
    .select("date, time_slot, countries, cities, horizontal_cover_url, is_published")
    .gte("date", startDate)
    .lte("date", endDate)
    .eq("is_published", true)
    .order("date", { ascending: true });

  if (error) {
    console.error("getArchiveSummary error:", error);
    return [];
  }

  // Group by date
  const grouped: Record<string, DaySummary> = {};
  for (const row of data) {
    if (!grouped[row.date]) {
      grouped[row.date] = {
        date: row.date,
        has_morning: false,
        has_afternoon: false,
        countries: [],
        cities: [],
        cover_url: null,
      };
    }
    const entry = grouped[row.date];
    if (row.time_slot === "morning") entry.has_morning = true;
    if (row.time_slot === "afternoon") entry.has_afternoon = true;
    // Merge countries/cities (deduplicate)
    if (row.countries) {
      for (const c of row.countries) {
        if (!entry.countries.includes(c)) entry.countries.push(c);
      }
    }
    if (row.cities) {
      for (const c of row.cities) {
        if (!entry.cities.includes(c)) entry.cities.push(c);
      }
    }
    if (!entry.cover_url && row.horizontal_cover_url) {
      entry.cover_url = row.horizontal_cover_url;
    }
  }

  return Object.values(grouped).sort((a, b) => a.date.localeCompare(b.date));
}

/** Get all unique dates with videos (for static generation) */
export async function getAllVideoDates(): Promise<string[]> {
  const { data, error } = await supabase
    .from("daily_videos")
    .select("date")
    .eq("is_published", true)
    .order("date", { ascending: false });

  if (error) {
    console.error("getAllVideoDates error:", error);
    return [];
  }

  // Deduplicate
  const seen = new Set<string>();
  const dates: string[] = [];
  for (const d of data) {
    if (!seen.has(d.date)) {
      seen.add(d.date);
      dates.push(d.date);
    }
  }
  return dates;
}
