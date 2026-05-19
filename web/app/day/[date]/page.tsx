import { Metadata } from "next";
import Link from "next/link";
import { getVideosByDate, getAllVideoDates } from "@/lib/database";
import VideoSection from "@/components/video/VideoSection";
import { LocationList } from "@/components/home/LocationList";
import { ArrowLeft, ArrowRight } from "lucide-react";
import type { DailyVideo } from "@/types";

interface DayPageProps {
  params: { date: string };
}

export async function generateStaticParams() {
  const dates = await getAllVideoDates();
  return dates.map((date) => ({ date }));
}

export const dynamicParams = true; // ISR fallback for dates not pre-generated

export const revalidate = 86400; // Revalidate daily for history pages

export async function generateMetadata({
  params,
}: DayPageProps): Promise<Metadata> {
  return {
    title: params.date,
  };
}

function formatDateDisplay(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });
}

function getAdjacentDates(dateStr: string): {
  prev: string | null;
  next: string | null;
} {
  const date = new Date(dateStr + "T00:00:00");
  const prev = new Date(date);
  prev.setDate(prev.getDate() - 1);
  const next = new Date(date);
  next.setDate(next.getDate() + 1);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return {
    prev: prev.toISOString().split("T")[0],
    next: next <= today ? next.toISOString().split("T")[0] : null,
  };
}

export default async function DayPage({ params }: DayPageProps) {
  const videos: DailyVideo[] = await getVideosByDate(params.date);
  const { prev, next } = getAdjacentDates(params.date);

  const morningVideo =
    videos.find((v) => v.time_slot === "morning") ?? null;
  const afternoonVideo =
    videos.find((v) => v.time_slot === "afternoon") ?? null;

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      {/* Navigation */}
      <div className="flex items-center justify-between mb-12">
        <div className="flex items-center gap-4">
          {prev ? (
            <Link
              href={`/day/${prev}`}
              className="flex items-center gap-1 text-xs text-earth-500 hover:text-earth-blue transition-colors"
            >
              <ArrowLeft className="w-3 h-3" />
              {prev}
            </Link>
          ) : (
            <span className="w-24" />
          )}
        </div>

        <h1 className="text-xl font-serif text-earth-100 text-center">
          {formatDateDisplay(params.date)}
        </h1>

        <div className="flex items-center gap-4">
          {next ? (
            <Link
              href={`/day/${next}`}
              className="flex items-center gap-1 text-xs text-earth-500 hover:text-earth-blue transition-colors"
            >
              {next}
              <ArrowRight className="w-3 h-3" />
            </Link>
          ) : (
            <span className="w-24" />
          )}
        </div>
      </div>

      {videos.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <p className="text-earth-500 text-sm">No videos for this date.</p>
          <Link
            href="/archive"
            className="mt-4 text-xs text-earth-blue hover:text-earth-100 transition-colors"
          >
            Back to Archive
          </Link>
        </div>
      )}

      {morningVideo && (
        <section className="mb-16">
          <VideoSection video={morningVideo} />
        </section>
      )}

      {morningVideo && afternoonVideo && (
        <div className="flex items-center gap-4 mb-16">
          <div className="flex-1 h-px bg-earth-700" />
          <span className="text-[10px] tracking-[.3em] uppercase text-earth-600">
            &middot;
          </span>
          <div className="flex-1 h-px bg-earth-700" />
        </div>
      )}

      {afternoonVideo && (
        <section className="mb-16">
          <VideoSection video={afternoonVideo} />
        </section>
      )}

      {videos.length > 0 && <LocationList videos={videos} />}

      {/* Back link */}
      <div className="mt-12 text-center">
        <Link
          href="/archive"
          className="text-xs tracking-widest uppercase text-earth-blue hover:text-earth-100 transition-colors"
        >
          Back to Archive &rarr;
        </Link>
      </div>
    </div>
  );
}
