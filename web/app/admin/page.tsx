"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@supabase/supabase-js";
import { VideoUploadForm } from "@/components/admin/VideoUploadForm";
import { VideoList } from "@/components/admin/VideoList";
import { Button } from "@/components/ui/Button";
import { SITE } from "@/lib/constants";
import type { DailyVideo } from "@/types";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export default function AdminPage() {
  const router = useRouter();
  const [authed, setAuthed] = useState(false);
  const [checking, setChecking] = useState(true);
  const [videos, setVideos] = useState<DailyVideo[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Check auth on mount
  useEffect(() => {
    const hasToken = document.cookie.includes("admin_token=");
    if (!hasToken) {
      router.push("/admin/login");
    } else {
      setAuthed(true);
    }
    setChecking(false);
  }, [router]);

  // Load videos
  const loadVideos = useCallback(async () => {
    const { data, error } = await supabase
      .from("daily_videos")
      .select("*")
      .order("date", { ascending: false })
      .order("time_slot", { ascending: true })
      .limit(30);

    if (!error && data) {
      setVideos(data as DailyVideo[]);
    }
  }, []);

  useEffect(() => {
    if (authed) {
      loadVideos();
    }
  }, [authed, loadVideos]);

  const handleUpload = async (
    formData: {
      date: string;
      time_slot: "morning" | "afternoon";
      title: string;
      countries: string;
      cities: string;
    },
    files: { horizontalVideo: File | null; horizontalCover: File | null }
  ) => {
    setLoading(true);
    setMessage(null);

    try {
      let videoUrl: string | null = null;
      let coverUrl: string | null = null;

      // Upload video
      if (files.horizontalVideo) {
        const videoPath = `videos/horizontal/${formData.date}-${formData.time_slot}.mp4`;
        const { error: videoErr } = await supabase.storage
          .from("videos")
          .upload(videoPath, files.horizontalVideo, { upsert: true });

        if (videoErr) throw videoErr;

        const { data: videoPublic } = supabase.storage
          .from("videos")
          .getPublicUrl(videoPath);
        videoUrl = videoPublic.publicUrl;
      }

      // Upload cover
      if (files.horizontalCover) {
        const coverPath = `covers/horizontal/${formData.date}-${formData.time_slot}.jpg`;
        const { error: coverErr } = await supabase.storage
          .from("covers")
          .upload(coverPath, files.horizontalCover, { upsert: true });

        if (coverErr) throw coverErr;

        const { data: coverPublic } = supabase.storage
          .from("covers")
          .getPublicUrl(coverPath);
        coverUrl = coverPublic.publicUrl;
      }

      // Insert database record
      const countries = formData.countries
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const cities = formData.cities
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const { error: insertErr } = await supabase.from("daily_videos").upsert(
        {
          date: formData.date,
          time_slot: formData.time_slot,
          title: formData.title || null,
          horizontal_video_url: videoUrl,
          horizontal_cover_url: coverUrl,
          countries,
          cities,
          sources_used: [],
          is_published: true,
        },
        { onConflict: "date,time_slot" }
      );

      if (insertErr) throw insertErr;

      setMessage({ type: "success", text: "Video uploaded and published!" });
      await loadVideos();

      // Trigger revalidation
      await fetch("/api/revalidate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-revalidate-secret": process.env.NEXT_PUBLIC_REVALIDATE_SECRET || "",
        },
        body: JSON.stringify({ paths: ["/", "/archive"] }),
      });
    } catch (err) {
      console.error("Upload error:", err);
      setMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Upload failed",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePublish = async (id: string, currentStatus: boolean) => {
    setLoading(true);
    const { error } = await supabase
      .from("daily_videos")
      .update({ is_published: !currentStatus })
      .eq("id", id);

    if (!error) {
      await loadVideos();
    }
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this video?")) return;

    setLoading(true);
    const { error } = await supabase.from("daily_videos").delete().eq("id", id);

    if (!error) {
      await loadVideos();
    }
    setLoading(false);
  };

  const handleLogout = () => {
    document.cookie = "admin_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    router.push("/admin/login");
  };

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-earth-900">
        <div className="w-3 h-3 rounded-full bg-earth-blue animate-pulse" />
      </div>
    );
  }

  if (!authed) return null;

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-xl font-serif text-earth-100">
            {SITE.name} Admin
          </h1>
          <p className="text-xs text-earth-500 mt-1">
            Manage videos, covers, and publication
          </p>
        </div>
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          Logout
        </Button>
      </div>

      {/* Message */}
      {message && (
        <div
          className={`mb-6 p-4 rounded-md text-sm ${
            message.type === "success"
              ? "bg-green-900/30 border border-green-800 text-green-300"
              : "bg-red-900/30 border border-red-800 text-red-300"
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Upload Form */}
      <div className="mb-8">
        <VideoUploadForm onSubmit={handleUpload} loading={loading} />
      </div>

      {/* Video List */}
      <VideoList
        videos={videos}
        onTogglePublish={handleTogglePublish}
        onDelete={handleDelete}
        loading={loading}
      />
    </div>
  );
}
