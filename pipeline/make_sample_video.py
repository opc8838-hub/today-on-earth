# -*- coding: utf-8 -*-
"""Build an internal Today on Earth sample video.

This script is intentionally separate from the production renderer. It creates
private test renders from a small, rights-marked source list so the visual
language can be tuned before formal source licensing.

Usage:
    python make_sample_video.py --count 3 --duration 5
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import urllib.request
from urllib.parse import urlencode
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml


WORK = Path(__file__).resolve().parent
SOURCES_FILE = WORK / "sample_sources.yaml"
OUTPUT_ROOT = Path("C:/tmp/today-on-earth-samples")

CANVAS_W = 1920
CANVAS_H = 1080
FPS = 30

FONT = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")


def find_exe(name: str, extra: list[str] | None = None) -> str:
    found = shutil.which(name)
    if found:
        return found

    for candidate in extra or []:
        path = Path(candidate)
        if path.exists():
            return str(path)

    raise FileNotFoundError(f"Cannot find {name}. Add it to PATH or install it.")


FFMPEG = find_exe(
    "ffmpeg",
    [
        "C:/Users/Administrator/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe",
        str(WORK / "ffmpeg.exe"),
    ],
)
FFPROBE = find_exe(
    "ffprobe",
    [
        "C:/Users/Administrator/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffprobe.exe",
    ],
)
YTDLP = find_exe("yt-dlp")


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def ff_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", r"\:")


def escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", r"\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
        .replace("%", r"\%")
        .replace("\n", " ")
    )


def drawtext(
    text: str,
    x: str | int,
    y: str | int,
    size: int,
    color: str = "white",
    font: Path = FONT,
    alpha: float | None = None,
) -> str:
    opts = [
        f"fontfile='{ff_path(font)}'",
        f"text='{escape_drawtext(text)}'",
        "expansion=none",
        f"x={x}",
        f"y={y}",
        f"fontsize={size}",
        f"fontcolor={color}",
        "shadowcolor=black@0.35",
        "shadowx=1",
        "shadowy=1",
    ]
    if alpha is not None:
        opts.append(f"alpha={alpha}")
    return "drawtext=" + ":".join(opts)


def glass_text(text: str, x: str | int, y: str | int, size: int, color: str = "0x063451ff") -> str:
    return drawtext(text, x, y, size, color, FONT_BOLD)


def slide_x(target: int, distance: int = 1850, duration: float = 0.45) -> str:
    """FFmpeg expression: slide from left into target x."""
    return f"'{target}-max(0\\,0.45-t)*{distance / duration:.1f}'"


def load_sources() -> list[dict]:
    with SOURCES_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [
        s
        for s in data["sources"]
        if s.get("status") == "active" and not s.get("has_burned_overlays")
    ]


def local_time(source: dict) -> str:
    tz_name = source.get("timezone") or "UTC"
    try:
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        now = datetime.utcnow()
    return now.strftime("%H:%M")


def get_weather(source: dict) -> dict:
    fallback = source.get("weather") or {}
    lat = source.get("latitude")
    lon = source.get("longitude")
    if lat is None or lon is None:
        return {
            "temp_c": fallback.get("temp_c", 17),
            "wind_kmh": fallback.get("wind_kmh", 10),
            "humidity": fallback.get("humidity", 73),
        }

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": source.get("timezone") or "UTC",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TodayOnEarth/0.1"})
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
        current = payload["current"]
        return {
            "temp_c": round(float(current.get("temperature_2m", fallback.get("temp_c", 17)))),
            "wind_kmh": round(float(current.get("wind_speed_10m", fallback.get("wind_kmh", 10)))),
            "humidity": round(float(current.get("relative_humidity_2m", fallback.get("humidity", 73)))),
            "weather_code": current.get("weather_code"),
        }
    except Exception as exc:
        print(f"  weather fallback for {source['id']}: {exc}")
        return {
            "temp_c": fallback.get("temp_c", 17),
            "wind_kmh": fallback.get("wind_kmh", 10),
            "humidity": fallback.get("humidity", 73),
        }


def get_stream_url(source: dict) -> str:
    if source.get("platform") == "youtube_live":
        result = run(
            [
                YTDLP,
                "-g",
                "--no-warnings",
                "-f",
                "best[height<=1080]/best",
                source["url"],
            ],
            timeout=45,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip()[-500:])
        urls = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not urls:
            raise RuntimeError("yt-dlp returned no stream URL")
        return urls[-1]

    if source.get("platform") == "skyline_page":
        req = urllib.request.Request(
            source["url"],
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(req, timeout=25) as response:
            html = response.read().decode("utf-8", "replace")

        match = re.search(
            r"(?:url|source)\s*:\s*([\"'])(?:livee\.m3u8(?P<a_param>\?a=\w+))\1",
            html,
        )
        if not match:
            raise RuntimeError("Cannot extract Skyline live token from page")
        return "https://hd-auth.skylinewebcams.com/live.m3u8" + match.group("a_param")

    return source["url"]


def capture_and_render(source: dict, index: int, out_dir: Path, duration: int) -> Path:
    stream_url = get_stream_url(source)
    output = out_dir / f"clip_{index:02d}_{source['id']}.mp4"

    city_cn = source.get("city_cn") or source.get("city")
    country_cn = source.get("country_cn") or source.get("country")
    city_en = source.get("city")
    country_en = source.get("country")
    city_label = city_en if city_en == city_cn else f"{city_en} {city_cn}"
    country_label = country_en if country_en == country_cn else f"{country_en} {country_cn}"
    time_line = f"Local time {local_time(source)}"
    weather = get_weather(source)
    temp_c = weather.get("temp_c", 17)
    wind_kmh = weather.get("wind_kmh", 10)
    humidity = weather.get("humidity", 73)
    rendered_local_time = local_time(source)
    source["_render_weather"] = weather
    source["_render_local_time"] = rendered_local_time
    top_alpha = "'if(lt(t,0.18),0,if(lt(t,0.55),(t-0.18)/0.37,if(lt(t,%0.2f),1,(%0.2f-t)/0.45)))'" % (
        max(duration - 0.45, 0.55),
        duration,
    )

    filters = [
        "scale=1920:1080:force_original_aspect_ratio=increase",
        "crop=1920:1080",
        "fps=30",
        "eq=contrast=1.04:brightness=0.015:saturation=1.04",
        "hqdn3d=luma_spatial=1.5:chroma_spatial=2:luma_tmp=2",
        "unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=0.35",
        f"fade=t=in:st=0:d=0.18,fade=t=out:st={max(duration - 0.20, 0)}:d=0.20",
        # Top glass panel, matching the supplied mockup.
        f"drawbox=x={slide_x(145)}:y=82:w=1675:h=165:color=white@0.76:t=fill",
        f"drawbox=x={slide_x(145)}:y=82:w=1675:h=1:color=white@0.95:t=fill",
        f"drawbox=x={slide_x(145)}:y=246:w=1675:h=1:color=0x95bed2aa:t=fill",
        # Blue lower band in the glass panel.
        f"drawbox=x={slide_x(318)}:y=164:w=1040:h=56:color=0x65b8ddaa:t=fill",
        f"drawbox=x={slide_x(318)}:y=164:w=1040:h=1:color=white@0.65:t=fill",
        # Globe stand-in. Kept vector/text based so the sample renderer has no asset dependency.
        drawtext("◎", slide_x(155), 66, 168, "0x50add8ff", FONT_BOLD, alpha=top_alpha),
        drawtext("EARTH", slide_x(184), 171, 18, "0xffffffff", FONT_BOLD, alpha=top_alpha),
        drawtext(city_label, slide_x(350), 109, 40, "0x063451ff", FONT_BOLD, alpha=top_alpha),
        drawtext(country_label, slide_x(620), 109, 40, "0x063451ff", FONT_BOLD, alpha=top_alpha),
        drawtext("TEMP", slide_x(372), 183, 20, "0xffffffff", FONT_BOLD, alpha=top_alpha),
        drawtext(f"{temp_c}°C", slide_x(452), 179, 30, "0xffffffff", FONT, alpha=top_alpha),
        drawtext("WIND", slide_x(610), 183, 20, "0xffffffff", FONT_BOLD, alpha=top_alpha),
        drawtext(f"{wind_kmh} km/h", slide_x(690), 179, 30, "0xffffffff", FONT, alpha=top_alpha),
        drawtext("HUM", slide_x(890), 183, 20, "0xffffffff", FONT_BOLD, alpha=top_alpha),
        drawtext(f"{humidity}%", slide_x(955), 179, 30, "0xffffffff", FONT, alpha=top_alpha),
        drawtext("TIME", slide_x(1110), 183, 20, "0xffffffff", FONT_BOLD, alpha=top_alpha),
        drawtext(rendered_local_time, slide_x(1184), 179, 30, "0xffffffff", FONT, alpha=top_alpha),
        drawtext("Today on Earth", "w-text_w-170", 157, 36, "0x063451ff", FONT_BOLD, alpha=top_alpha),
        drawtext("⌒  ·  ⌒", "w-text_w-215", 112, 38, "0x237da4aa", FONT, alpha=top_alpha),
    ]

    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-user_agent",
        "Mozilla/5.0",
        "-i",
        stream_url,
        "-t",
        str(duration),
        "-vf",
        ",".join(filters),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    result = run(cmd, timeout=max(90, duration * 20))
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-1000:])

    return output


def concat_clips(clips: list[Path], out_dir: Path) -> Path:
    concat_file = out_dir / "concat.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{str(clip).replace('\\', '/')}'\n")

    output = out_dir / "today-on-earth-sample-horizontal.mp4"
    result = run(
        [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(output),
        ],
        timeout=90,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-1000:])
    return output


def make_cover(video: Path, out_dir: Path) -> Path:
    cover = out_dir / "today-on-earth-sample-cover.jpg"
    result = run(
        [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            "00:00:02",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(cover),
        ],
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-1000:])
    return cover


def write_manifest(out_dir: Path, sources: list[dict], video: Path, cover: Path, duration: int) -> None:
    manifest = {
        "project": "Today on Earth",
        "render_type": "internal_sample",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "rights_note": "Internal visual test only. Sources marked permission_needed are not cleared for public/commercial release.",
        "duration_seconds": len(sources) * duration,
        "horizontal_video": str(video),
        "cover": str(cover),
        "sources": [
            {
                "id": s["id"],
                "title": s.get("title"),
                "url": s["url"],
                "provider": s.get("provider"),
                "rights_status": s.get("rights_status"),
                "usage_mode": s.get("usage_mode"),
                "credit": s.get("credit"),
                "latitude": s.get("latitude"),
                "longitude": s.get("longitude"),
                "timezone": s.get("timezone"),
                "local_time": s.get("_render_local_time"),
                "weather": s.get("_render_weather"),
            }
            for s in sources
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = OUTPUT_ROOT / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources()
    selected = random.sample(sources, min(args.count, len(sources)))

    print(f"Output: {out_dir}")
    print(f"FFmpeg: {FFMPEG}")
    print("Selected sources:")
    for source in selected:
        print(f"  - {source['id']} ({source.get('provider')})")

    clips: list[Path] = []
    errors: list[dict] = []
    for index, source in enumerate(selected, start=1):
        print(f"\n[{index}/{len(selected)}] Capturing {source['id']}...")
        try:
            clip = capture_and_render(source, index, out_dir, args.duration)
            clips.append(clip)
            print(f"  ok: {clip.name}")
        except Exception as exc:
            errors.append({"source": source["id"], "error": str(exc)})
            print(f"  failed: {exc}")

    if not clips:
        (out_dir / "errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("No clips rendered.")
        return 1

    video = concat_clips(clips, out_dir)
    cover = make_cover(video, out_dir)
    write_manifest(out_dir, selected, video, cover, args.duration)

    if errors:
        (out_dir / "errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print("\nDone.")
    print(f"Video: {video}")
    print(f"Cover: {cover}")
    print(f"Manifest: {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONUTF8", "1")
    raise SystemExit(main())
