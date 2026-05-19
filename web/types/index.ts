// Today on Earth — TypeScript Types

export interface DailyVideo {
  id: string;
  date: string; // YYYY-MM-DD
  time_slot: "morning" | "afternoon";
  title: string | null;
  horizontal_video_url: string | null;
  vertical_video_url: string | null;
  horizontal_cover_url: string | null;
  vertical_cover_url: string | null;
  countries: string[];
  cities: string[];
  sources_used: string[];
  is_published: boolean;
  created_at: string;
}

export interface VideoSource {
  id: string;
  url: string;
  platform: string | null;
  country: string | null;
  country_cn: string | null;
  city: string | null;
  city_cn: string | null;
  timezone: string | null;
  scene: string | null;
  quality: number | null;
  status: string;
  is_mandatory: boolean;
  last_checked: string | null;
}

export interface DayVideos {
  date: string;
  morning: DailyVideo | null;
  afternoon: DailyVideo | null;
}

export interface ArchiveMonth {
  year: number;
  month: number; // 1-12
  days: DaySummary[];
}

export interface DaySummary {
  date: string;
  has_morning: boolean;
  has_afternoon: boolean;
  countries: string[];
  cities: string[];
  cover_url: string | null;
}
