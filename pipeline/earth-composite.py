# -*- coding: utf-8 -*-
"""Today on Earth — Video Renderer
====================================
Reads sources.yaml → selects 5 random active sources →
downloads 5-6s clips → composites with branded layout →
outputs final 30s video.

Usage:
    python earth-composite.py                    # random 5 from active
    python earth-composite.py --sources tokyo_live_camera,dubai_webcam,...  # specific
    python earth-composite.py --duration 6 --count 5  # custom settings
"""
import subprocess, sys, os, yaml, random, json
from datetime import datetime, timezone
from pathlib import Path

# === CONFIG ============================================================
WORK = Path(__file__).resolve().parent
SOURCES_FILE = WORK / "sources.yaml"
OUTPUT_DIR = Path("C:/tmp/earth-render")
FONT_FILE = Path("C:/tmp/earth-test/font.ttc")  # Chinese-capable font
FONT_BOLD = FONT_FILE  # same font, different weight via FFmpeg

CANVAS_W, CANVAS_H = 1920, 1080
CLIP_DURATION = 6           # seconds per clip
NUM_CLIPS = 5               # clips per video
OUTPUT_NAME = "Today_on_Earth.mp4"

# Layout coordinates (1920×1080)
HEADER_Y, HEADER_H = 0, 130
SEPARATOR_Y = 131
VIDEO_Y, VIDEO_H = 155, 700     # 16:9 → 1244×700
VIDEO_W = int(VIDEO_H * 16 / 9)  # 1244
VIDEO_X = (CANVAS_W - VIDEO_W) // 2  # 338
INFOBAR_Y, INFOBAR_H = 870, 110
SLOGAN_Y = 990

# Colors
WHITE = "0xffffffff"
WARM_WHITE = "0xfff5f0e6"
GOLD = "0xffd4b872"
DARK_BG = "0xff1a1a2e"
TEXT_PRIMARY = "0xffffffff"
TEXT_SECONDARY = "0xffa0a0b0"
TEXT_GOLD = "0xffd4b872"

# === HELPERS ===========================================================

def load_sources():
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [s for s in data["sources"] if s.get("status") == "active"]

def select_sources(sources, n=5):
    """Pick n sources, preferring diversity across scenes and timezones."""
    if len(sources) <= n:
        return sources
    selected = []
    # Try to cover different scenes
    scenes = {}
    for s in sources:
        scene = s.get("scene", "city")
        scenes.setdefault(scene, []).append(s)
    # Round-robin from different scenes
    scene_keys = list(scenes.keys())
    random.shuffle(scene_keys)
    while len(selected) < n and scene_keys:
        for scene in scene_keys:
            pool = scenes[scene]
            if pool:
                pick = random.choice(pool)
                if pick not in selected:
                    selected.append(pick)
                    pool.remove(pick)
            if len(selected) >= n:
                break
        # Fill remaining from any scene
        if len(selected) < n:
            remaining = [s for s in sources if s not in selected]
            random.shuffle(remaining)
            selected.extend(remaining[:n - len(selected)])
    return selected[:n]

def get_local_time(tz_str):
    """Get approximate local time for a timezone. Returns (hour, minute, is_day)."""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_str)
        now = datetime.now(tz)
        return now.hour, now.minute, 6 <= now.hour < 20
    except:
        return 12, 0, True

def get_mock_weather(city, scene):
    """Mock weather based on scene type. Will be replaced by OpenWeatherMap API."""
    mock_data = {
        "city":      ("🌤", 23, 72),
        "beach":     ("☀️", 28, 65),
        "mountain":  ("⛅", 12, 55),
        "underwater":("🌊", 22, 95),
        "desert":    ("☀️", 35, 20),
        "harbor":    ("🌤", 20, 70),
        "landmark":  ("🌤", 24, 60),
        "wildlife":  ("☀️", 26, 50),
        "lake":      ("⛅", 18, 58),
        "volcano":   ("🌋", 20, 80),
        "bay":       ("🌤", 22, 68),
        "nature":    ("⛅", 15, 55),
    }
    return mock_data.get(scene, ("🌤", 22, 60))

def ffmpeg_drawtext(text, x, y, fontsize=32, fontcolor=TEXT_PRIMARY,
                    fontfile=None, alpha=1.0, align="left", shadow=True):
    """Build FFmpeg drawtext filter string."""
    if fontfile is None:
        fontfile = str(FONT_FILE).replace("\\", "/").replace(":", "\\\\:")

    opts = [
        f"text='{text}'",
        f"fontfile='{fontfile}'",
        f"fontsize={fontsize}",
        f"fontcolor={fontcolor}",
    ]
    if alpha < 1.0:
        opts.append(f"alpha={alpha}")
    if align == "center":
        opts.append(f"x=(w-text_w)/2:{y}")
    elif align == "right":
        opts.append(f"x=w-text_w-{x}:{y}")
    else:
        opts.append(f"x={x}:{y}")
    if shadow:
        opts.append("shadowcolor=black@0.5:shadowx=2:shadowy=2")
    return "drawtext=" + ":".join(opts)

# === DOWNLOAD ==========================================================

def download_clip(source, output_path):
    """Download 6s clip from a YouTube live source using yt-dlp."""
    url = source["url"]
    tmp_path = str(output_path).replace(".mp4", "_raw.mp4")

    cmd = [
        "yt-dlp",
        "--no-part",
        "--downloader", "ffmpeg",
        "--hls-use-mpegts",
        "-f", "best[height<=1080]",  # best up to 1080p
        "-o", tmp_path,
        url
    ]

    # Use ffmpeg to trim to exact duration after download
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ⚠ yt-dlp warning: {result.stderr[:100]}")
    except subprocess.TimeoutExpired:
        print(f"  ⚠ Download timeout for {source['id']}")
        return None

    # Trim to exact duration
    if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 10000:
        trim_cmd = [
            "ffmpeg", "-y", "-i", tmp_path,
            "-t", str(CLIP_DURATION),
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k",
            "-crf", "18",
            str(output_path)
        ]
        subprocess.run(trim_cmd, capture_output=True, timeout=20)
        os.remove(tmp_path)
        return output_path
    return None

# === COMPOSITE =========================================================

def composite_clip(raw_clip, source, output_path, index):
    """Apply branded layout to a single clip."""
    city = source.get("city_cn", source.get("city", "Unknown"))
    country = source.get("country_cn", source.get("country", ""))
    scene = source.get("scene", "city")
    tz = source.get("timezone", "UTC")

    hour, minute, is_day = get_local_time(tz)
    weather_icon, temp, humidity = get_mock_weather(city, scene)

    now = datetime.now()
    date_str = now.strftime("%Y/%m/%d")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]
    date_display = f"{date_str} {weekday_cn}"

    location_line = f"{city}, {country}"
    info_line = f"{weather_icon} {temp}°C    湿度 {humidity}%    当地时间 {hour:02d}:{minute:02d}"

    # Build FFmpeg filter chain
    filters = []

    # === 0. Video quality enhancement (before layout) =================
    # Applied to raw footage to handle varying lighting conditions:
    # - Night/dark scenes → gentle brighten + denoise
    # - Overcast → contrast recovery
    # - All scenes → subtle sharpen for texture
    filters.append(
        # Normalize brightness (stretch histogram, 2% clipping to avoid outliers)
        "normalize=blackpt=black:whitept=white:smoothing=40,"
        # Subtle contrast boost
        "eq=contrast=1.08:brightness=0.02,"
        # Color: slight warmth + saturation
        "eq=saturation=1.10,"
        # Denoise (light touch, mainly helps dark scenes)
        "hqdn3d=luma_spatial=2:chroma_spatial=4:luma_tmp=3,"
        # Subtle sharpen for texture
        "unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=0.6:"
                "chroma_msize_x=5:chroma_msize_y=5:chroma_amount=0.3"
    )

    # === 1. Scale and pad video to fit video area =====================
    filters.append(
        f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_W}:{VIDEO_H}:(ow-iw)/2:(oh-ih)/2:black"
    )

    # 2. Pad to full canvas
    filters.append(
        f"pad={CANVAS_W}:{CANVAS_H}:{VIDEO_X}:{VIDEO_Y}:black"
    )

    # 3. White header background
    filters.append(
        f"drawbox=x=0:y={HEADER_Y}:w={CANVAS_W}:h={HEADER_H}:color={WARM_WHITE}:t=fill"
    )

    # 4. Gold separator line
    filters.append(
        f"drawbox=x=0:y={SEPARATOR_Y}:w={CANVAS_W}:h=2:color={GOLD}:t=fill"
    )

    # 5. Header text — Brand
    brands = [
        ffmpeg_drawtext("今日地球", 80, 35, fontsize=40,
                        fontcolor=TEXT_GOLD, shadow=False),
        ffmpeg_drawtext("Today on Earth", 80, 80, fontsize=18,
                        fontcolor="0xff808090", shadow=False),
        ffmpeg_drawtext(date_display, 100, 50, fontsize=22,
                        fontcolor="0xff505060", align="right", shadow=False),
    ]
    filters.extend(brands)

    # 6. InfoBar background
    filters.append(
        f"drawbox=x=0:y={INFOBAR_Y}:w={CANVAS_W}:h={INFOBAR_H}:color={DARK_BG}:t=fill"
    )

    # 7. InfoBar bottom line (gold accent)
    filters.append(
        f"drawbox=x=80:y={INFOBAR_Y + INFOBAR_H - 2}:w=200:h=2:color={GOLD}:t=fill"
    )

    # 8. InfoBar text
    info_texts = [
        ffmpeg_drawtext(location_line, 80, INFOBAR_Y + 20, fontsize=36,
                        fontcolor=TEXT_PRIMARY, shadow=False),
        ffmpeg_drawtext(info_line, 80, INFOBAR_Y + 68, fontsize=22,
                        fontcolor=TEXT_SECONDARY, shadow=False),
    ]
    filters.extend(info_texts)

    # 9. Slogan
    filters.append(
        ffmpeg_drawtext("把世界重新打开给下一代", 0, SLOGAN_Y,
                        fontsize=18, fontcolor="0xff404055",
                        align="center", shadow=False, alpha=0.7)
    )

    # 10. "Inspired by earthTV" small credit at bottom right
    filters.append(
        ffmpeg_drawtext("Inspired by earthTV®", 100, SLOGAN_Y + 30,
                        fontsize=12, fontcolor="0xff303040",
                        align="right", shadow=False, alpha=0.4)
    )

    filter_chain = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_clip),
        "-vf", filter_chain,
        "-c:v", "libx264", "-preset", "slow",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "copy",
        "-t", str(CLIP_DURATION),
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  ❌ FFmpeg error: {result.stderr[-300:]}")
        return None
    return output_path

# === CONCATENATE =======================================================

def concat_clips(clip_paths, output_path):
    """Concatenate all composited clips into final video."""
    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{p}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    return output_path

# === MAIN ==============================================================

def main():
    # Parse args
    specific_ids = None
    for arg in sys.argv[1:]:
        if arg.startswith("--sources="):
            specific_ids = arg.split("=", 1)[1].split(",")
        elif arg.startswith("--duration="):
            global CLIP_DURATION
            CLIP_DURATION = int(arg.split("=", 1)[1])
        elif arg.startswith("--count="):
            global NUM_CLIPS
            NUM_CLIPS = int(arg.split("=", 1)[1])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load and select sources
    all_sources = load_sources()
    if specific_ids:
        selected = [s for s in all_sources if s["id"] in specific_ids]
        print(f"Using {len(selected)} specified sources")
    else:
        selected = select_sources(all_sources, NUM_CLIPS)
        print(f"Selected {len(selected)} random sources from {len(all_sources)} active")

    for i, s in enumerate(selected):
        scene_tag = f"[{s.get('scene', '?')}]"
        print(f"  {i+1}. {s['city_cn']}, {s['country_cn']} {scene_tag} (q={s.get('quality', '?')})")

    # Phase 1: Download clips
    print("\n📥 Downloading clips...")
    raw_clips = []
    for i, src in enumerate(selected):
        clip_path = OUTPUT_DIR / f"clip_{i+1:02d}_raw.mp4"
        print(f"  [{i+1}/{len(selected)}] {src['city_cn']}...", end=" ", flush=True)
        result = download_clip(src, clip_path)
        if result:
            size_mb = os.path.getsize(result) / 1024 / 1024
            print(f"✅ {size_mb:.1f}MB")
            raw_clips.append((result, src, i+1))
        else:
            print("❌ Failed")

    if not raw_clips:
        print("No clips downloaded. Aborting.")
        return

    # Phase 2: Composite each clip
    print("\n🎨 Compositing with branded layout...")
    composited = []
    for raw_path, src, idx in raw_clips:
        comp_path = OUTPUT_DIR / f"clip_{idx:02d}_comp.mp4"
        print(f"  [{idx}/{len(raw_clips)}] {src['city_cn']}...", end=" ", flush=True)
        result = composite_clip(raw_path, src, comp_path, idx)
        if result:
            print("✅")
            composited.append(result)
        else:
            print("❌")

    if not composited:
        print("No clips composited. Aborting.")
        return

    # Phase 3: Concatenate
    print("\n🔗 Concatenating final video...")
    final_path = OUTPUT_DIR / OUTPUT_NAME
    concat_clips(composited, final_path)

    if final_path.exists():
        size_mb = os.path.getsize(final_path) / 1024 / 1024
        duration = len(composited) * CLIP_DURATION
        print(f"\n✅ Done! {final_path}")
        print(f"   Duration: ~{duration}s | Size: {size_mb:.1f}MB | Sources: {len(composited)}")
    else:
        print("\n❌ Final video not created.")

if __name__ == "__main__":
    main()
