"use client";

import type { DailyVideo } from "@/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

interface VideoListProps {
  videos: DailyVideo[];
  onTogglePublish: (id: string, currentStatus: boolean) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  loading: boolean;
}

export function VideoList({
  videos,
  onTogglePublish,
  onDelete,
  loading,
}: VideoListProps) {
  if (videos.length === 0) {
    return (
      <div className="bg-earth-800 border border-earth-700 rounded-lg p-8 text-center">
        <p className="text-earth-500 text-sm">No videos uploaded yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-earth-800 border border-earth-700 rounded-lg overflow-hidden">
      <div className="px-6 py-3 border-b border-earth-700">
        <h2 className="text-sm font-medium text-earth-100 tracking-wider">
          Videos &middot; 视频列表
        </h2>
      </div>

      <div className="divide-y divide-earth-700">
        {videos.map((video) => (
          <div
            key={video.id}
            className="px-6 py-4 flex items-center justify-between gap-4"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-earth-300">
                  {video.date}
                </span>
                <Badge variant={video.time_slot === "morning" ? "gold" : "blue"}>
                  {video.time_slot}
                </Badge>
                <Badge variant={video.is_published ? "blue" : "default"}>
                  {video.is_published ? "published" : "draft"}
                </Badge>
              </div>
              <p className="text-sm text-earth-100 truncate">
                {video.title || `${video.time_slot} — ${video.date}`}
              </p>
              <p className="text-[10px] text-earth-500 mt-0.5">
                {video.cities?.join(", ") || "No cities"} &middot;{" "}
                {video.countries?.join(", ") || "No countries"}
              </p>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <Button
                size="sm"
                variant="outline"
                onClick={() => onTogglePublish(video.id, video.is_published)}
                disabled={loading}
              >
                {video.is_published ? "Unpublish" : "Publish"}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onDelete(video.id)}
                disabled={loading}
                className="text-red-400 hover:text-red-300"
              >
                Delete
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
