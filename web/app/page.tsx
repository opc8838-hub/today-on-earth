import { getTodayVideos } from "@/lib/database";
import { HeroBanner } from "@/components/home/HeroBanner";
import VideoSection from "@/components/video/VideoSection";
import { LocationList } from "@/components/home/LocationList";
import { SloganBar } from "@/components/home/SloganBar";
import type { DailyVideo } from "@/types";

export const revalidate = 3600; // ISR: revalidate every hour

export default async function HomePage() {
  const videos: DailyVideo[] = await getTodayVideos();

  const morningVideo =
    videos.find((v) => v.time_slot === "morning") ?? null;
  const afternoonVideo =
    videos.find((v) => v.time_slot === "afternoon") ?? null;

  const hasAnyVideo = morningVideo || afternoonVideo;

  return (
    <div className="max-w-6xl mx-auto px-6">
      <HeroBanner />

      {!hasAnyVideo && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-full bg-earth-800 border border-earth-700 flex items-center justify-center mb-6">
            <div className="w-3 h-3 rounded-full bg-earth-blue animate-pulse" />
          </div>
          <h2 className="text-xl font-serif text-earth-100 mb-2">
            Today&apos;s Earth Is Coming
          </h2>
          <p className="text-earth-500 text-sm max-w-sm">
            The first video of the day is being prepared. Come back soon to see
            what the world looks like right now.
          </p>
        </div>
      )}

      {/* Morning Earth */}
      {morningVideo && (
        <section className="mb-16">
          <VideoSection video={morningVideo} />
        </section>
      )}

      {/* Divider between morning and afternoon */}
      {morningVideo && afternoonVideo && (
        <div className="flex items-center gap-4 mb-16">
          <div className="flex-1 h-px bg-earth-700" />
          <span className="text-[10px] tracking-[.3em] uppercase text-earth-600">
            &middot;
          </span>
          <div className="flex-1 h-px bg-earth-700" />
        </div>
      )}

      {/* Afternoon Earth */}
      {afternoonVideo && (
        <section className="mb-16">
          <VideoSection video={afternoonVideo} />
        </section>
      )}

      {/* Location list */}
      {hasAnyVideo && <LocationList videos={videos} />}

      <SloganBar />
    </div>
  );
}
