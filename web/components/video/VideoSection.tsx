import type { DailyVideo } from "@/types";
import VideoPlayer from "./VideoPlayer";
import { VideoMeta } from "./VideoMeta";
import { LocationTags } from "./LocationTags";

interface VideoSectionProps {
  video: DailyVideo | null;
  className?: string;
}

export default function VideoSection({ video, className = "" }: VideoSectionProps) {
  if (!video || !video.horizontal_video_url) {
    return (
      <div
        className={`flex items-center justify-center bg-earth-800 border border-earth-700 rounded-lg aspect-video ${className}`}
      >
        <p className="text-earth-600 text-sm">
          {video ? "Video not yet available" : "Coming soon"}
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Video player */}
      <div className="aspect-video">
        <VideoPlayer
          src={video.horizontal_video_url}
          poster={video.horizontal_cover_url ?? undefined}
        />
      </div>

      {/* Metadata row */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <VideoMeta video={video} />
        <LocationTags
          countries={video.countries ?? []}
          cities={video.cities ?? []}
        />
      </div>
    </div>
  );
}
