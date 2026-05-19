import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

export async function GET() {
  try {
    const { data, error } = await supabase
      .from("daily_videos")
      .select("*")
      .eq("is_published", true)
      .order("date", { ascending: false })
      .limit(20);

    if (error) throw error;

    return NextResponse.json({ videos: data });
  } catch (err) {
    console.error("GET /api/videos error:", err);
    return NextResponse.json(
      { error: "Failed to fetch videos" },
      { status: 500 }
    );
  }
}
