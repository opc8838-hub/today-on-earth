import type { DailyVideo } from "@/types";
import { Badge } from "@/components/ui/Badge";

interface VideoMetaProps {
  video: DailyVideo;
  className?: string;
}

const TIME_SLOT_LABELS: Record<string, { en: string; cn: string }> = {
  morning: { en: "Morning Earth", cn: "早晨的地球" },
  afternoon: { en: "Afternoon Earth", cn: "下午的地球" },
};

export function VideoMeta({ video, className = "" }: VideoMetaProps) {
  const labels = TIME_SLOT_LABELS[video.time_slot] ?? {
    en: video.time_slot,
    cn: "",
  };

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <div className="flex items-center gap-3">
        <Badge variant="blue">{labels.en}</Badge>
        <span className="text-xs text-earth-300">{labels.cn}</span>
      </div>
      {video.title && (
        <h3 className="text-sm text-earth-100 font-medium">{video.title}</h3>
      )}
      <span className="text-[10px] text-earth-600 font-mono tracking-wider">
        {video.date}
      </span>
    </div>
  );
}
