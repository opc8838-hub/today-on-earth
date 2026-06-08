# -*- coding: utf-8 -*-
"""Build an internal Today on Earth sample video.

This script is intentionally separate from the production renderer. It creates
private test renders from a small, rights-marked source list so the visual
language can be tuned before formal source licensing.

Usage:
    python make_sample_video.py --count 8 --duration 5.5
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
import time
import urllib.request
from urllib.parse import urlencode
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from daily_record import append_run, load_record, today_key, used_source_ids
from render_top_overlay import render_overlay


WORK = Path(__file__).resolve().parent
SOURCES_FILE = WORK / "sample_sources.yaml"
OUTPUT_ROOT = Path("C:/tmp/today-on-earth-samples")

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
        "C:/Users/Administrator/.openclaw/tools/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe",
        "C:/Users/Administrator/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe",
        str(WORK / "ffmpeg.exe"),
    ],
)
FFPROBE = find_exe(
    "ffprobe",
    [
        "C:/Users/Administrator/.openclaw/tools/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffprobe.exe",
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


def load_sources(sources_file: Path = SOURCES_FILE) -> list[dict]:
    with sources_file.open("r", encoding="utf-8") as f:
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
        html = ""
        last_error: Exception | None = None
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "close",
        }
        for attempt in range(1, 5):
            try:
                req = urllib.request.Request(source["url"], headers=headers)
                with urllib.request.urlopen(req, timeout=45) as response:
                    html = response.read().decode("utf-8", "replace")
                break
            except Exception as exc:
                last_error = exc
                time.sleep(attempt * 2)

        if not html and shutil.which("curl"):
            result = run(
                [
                    "curl",
                    "-L",
                    "-A",
                    headers["User-Agent"],
                    "--max-time",
                    "45",
                    source["url"],
                ],
                timeout=60,
            )
            if result.returncode == 0:
                html = result.stdout

        match = re.search(
            r"(?:url|source)\s*:\s*([\"'])(?:livee\.m3u8(?P<a_param>\?a=\w+))\1",
            html,
        )
        if not match:
            raise RuntimeError(f"Cannot extract Skyline live token from page: {last_error}")
        return "https://hd-auth.skylinewebcams.com/live.m3u8" + match.group("a_param")

    return source["url"]


def capture_and_render(
    source: dict,
    index: int,
    out_dir: Path,
    duration: float,
    overlay_delay: float = 0.25,
) -> Path:
    stream_url = get_stream_url(source)
    output = out_dir / f"clip_{index:02d}_{source['id']}.mp4"
    overlay_path = out_dir / f"overlay_{index:02d}_{source['id']}.png"

    city_cn = source.get("city_cn") or source.get("city")
    country_cn = source.get("country_cn") or source.get("country")
    city_en = source.get("city")
    country_en = source.get("country")
    city_label = city_en if city_en == city_cn else f"{city_en} {city_cn}"
    country_label = country_en if country_en == country_cn else f"{country_en} {country_cn}"
    weather = get_weather(source)
    temp_c = weather.get("temp_c", 17)
    wind_kmh = weather.get("wind_kmh", 10)
    humidity = weather.get("humidity", 73)
    rendered_local_time = local_time(source)
    source["_render_weather"] = weather
    source["_render_local_time"] = rendered_local_time

    render_overlay(
        overlay_path,
        city_label=city_label,
        country_label=country_label,
        temp_c=temp_c,
        wind_kmh=wind_kmh,
        humidity=humidity,
        local_time=rendered_local_time,
    )

    base_filters = [
        "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos",
        "crop=1920:1080",
        "fps=30",
        "eq=contrast=1.04:brightness=0.015:saturation=1.04",
        "hqdn3d=luma_spatial=1.5:chroma_spatial=2:luma_tmp=2",
        "unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=0.35",
    ]
    overlay_fade_out = max(duration - 1.05, 1.35)
    overlay_in_duration = 1.10
    overlay_in_end = overlay_delay + overlay_in_duration
    filter_complex = (
        f"[0:v]{','.join(base_filters)}[base];"
        "[1:v]format=rgba,"
        f"fade=t=in:st={overlay_delay:.2f}:d={overlay_in_duration:.2f}:alpha=1,"
        f"fade=t=out:st={overlay_fade_out}:d=0.50:alpha=1[ov];"
        f"[base][ov]overlay=x=0:y='if(lt(t,{overlay_in_end:.2f}),-8+8*pow(min(max((t-{overlay_delay:.2f})/{overlay_in_duration:.2f}\\,0)\\,1)\\,0.55),0)':format=auto[v]"
    )

    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-filter_threads",
        "1",
        "-filter_complex_threads",
        "1",
        "-user_agent",
        "Mozilla/5.0",
        "-i",
        stream_url,
        "-loop",
        "1",
        "-i",
        str(overlay_path),
        "-t",
        str(duration),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-threads",
        "1",
        "-crf",
        "17",
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


def select_sources(sources: list[dict], count: int, used_ids: set[str]) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    available = [source for source in sources if source["id"] not in used_ids]
    if len(available) < count:
        warnings.append(
            f"Only {len(available)} unused active sources are available for today; "
            f"using {min(count, len(available))} without repeating."
        )

    pool = available
    random.shuffle(pool)

    selected: list[dict] = []
    selected_countries: set[str] = set()
    selected_cities: set[tuple[str | None, str | None]] = set()

    for source in pool:
        if len(selected) >= count:
            break
        country = source.get("country")
        city_key = (source.get("country"), source.get("city"))
        if country in selected_countries or city_key in selected_cities:
            continue
        selected.append(source)
        selected_countries.add(country)
        selected_cities.add(city_key)

    for source in pool:
        if len(selected) >= count:
            break
        if source in selected:
            continue
        city_key = (source.get("country"), source.get("city"))
        if city_key in selected_cities:
            continue
        selected.append(source)
        selected_cities.add(city_key)

    for source in pool:
        if len(selected) >= count:
            break
        if source not in selected:
            selected.append(source)

    return selected, warnings


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


def xfade_clips(clips: list[Path], out_dir: Path, clip_duration: float, transition_duration: float) -> Path:
    if len(clips) == 1 or transition_duration <= 0:
        return concat_clips(clips, out_dir)

    transition_duration = min(transition_duration, max(clip_duration - 0.2, 0.1))
    previous = clips[0]
    current_duration = clip_duration
    for idx, clip in enumerate(clips[1:], start=2):
        output = out_dir / f"xfade_step_{idx:02d}.mp4"
        offset = max(current_duration - transition_duration, 0.0)
        filter_complex = (
            "[0:v]setpts=PTS-STARTPTS,format=yuv420p[v0];"
            "[1:v]setpts=PTS-STARTPTS,format=yuv420p[v1];"
            f"[v0][v1]xfade=transition=fade:duration={transition_duration:.2f}:offset={offset:.2f}[v]"
        )
        result = run(
            [
                FFMPEG,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-filter_threads",
                "1",
                "-filter_complex_threads",
                "1",
                "-i",
                str(previous),
                "-i",
                str(clip),
                "-filter_complex",
                filter_complex,
                "-map",
                "[v]",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-threads",
                "1",
                "-crf",
                "17",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output),
            ],
            timeout=max(120, round(current_duration * 12)),
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip()[-1000:])
        previous = output
        current_duration += clip_duration - transition_duration

    final = out_dir / "today-on-earth-sample-horizontal.mp4"
    shutil.copy2(previous, final)
    return final


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
            "00:00:00.50",
            "-i",
            str(video),
            "-vf",
            "format=yuvj420p",
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


def write_manifest(
    out_dir: Path,
    sources: list[dict],
    video: Path,
    cover: Path,
    duration: float,
    transition_duration: float,
) -> None:
    estimated_duration = len(sources) * duration
    if len(sources) > 1:
        estimated_duration -= (len(sources) - 1) * transition_duration
    manifest = {
        "project": "Today on Earth",
        "render_type": "internal_sample",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "rights_note": "Internal visual test only. Sources marked permission_needed are not cleared for public/commercial release.",
        "clip_duration_seconds": duration,
        "transition_duration_seconds": transition_duration,
        "duration_seconds": round(estimated_duration, 2),
        "horizontal_video": str(video),
        "cover": str(cover),
        "sources": [
            {
                "id": s["id"],
                "title": s.get("title"),
                "city": s.get("city"),
                "city_cn": s.get("city_cn"),
                "country": s.get("country"),
                "country_cn": s.get("country_cn"),
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
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--duration", type=float, default=5.5)
    parser.add_argument("--transition", type=float, default=0.55)
    parser.add_argument("--first-overlay-delay", type=float, default=0.25)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--sources-file", type=Path, default=SOURCES_FILE)
    parser.add_argument("--slot", choices=["morning", "afternoon", "manual"], default="manual")
    parser.add_argument("--record-date", default=None)
    parser.add_argument("--avoid-daily-record", action="store_true")
    parser.add_argument("--record-daily-run", action="store_true")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = OUTPUT_ROOT / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources(args.sources_file)
    record_date = args.record_date or today_key()
    should_read_record = args.record_daily_run or args.avoid_daily_record
    used_ids = used_source_ids(load_record(record_date)) if should_read_record else set()
    selected, selection_warnings = select_sources(sources, min(args.count, len(sources)), used_ids)
    if len(selected) < args.count:
        print(f"Warning: requested {args.count} sources, but only {len(selected)} active sources are available.")
    for warning in selection_warnings:
        print(f"Warning: {warning}")

    print(f"Output: {out_dir}")
    print(f"FFmpeg: {FFMPEG}")
    print(f"Sources file: {args.sources_file}")
    print(f"Plan: {len(selected)} clips x {args.duration}s, {args.transition:.2f}s crossfade")
    if args.record_daily_run:
        print(f"Daily record: {record_date} / {args.slot}; skipping {len(used_ids)} used source(s)")
    print("Selected sources:")
    for source in selected:
        city = source.get("city") or source.get("city_cn") or "Unknown"
        city_cn = source.get("city_cn") or city
        country = source.get("country") or source.get("country_cn") or "Unknown"
        country_cn = source.get("country_cn") or country
        location = f"{city} {city_cn}, {country} {country_cn}"
        print(f"  - {source['id']} | {location} ({source.get('provider')})")

    clips: list[Path] = []
    errors: list[dict] = []
    for index, source in enumerate(selected, start=1):
        print(f"\n[{index}/{len(selected)}] Capturing {source['id']}...")
        last_error = None
        for attempt in range(1, max(args.attempts, 1) + 1):
            try:
                overlay_delay = args.first_overlay_delay if index == 1 else 0.25
                clip = capture_and_render(source, index, out_dir, args.duration, overlay_delay=overlay_delay)
                clips.append(clip)
                print(f"  ok: {clip.name}")
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                print(f"  attempt {attempt} failed: {exc}")
        if last_error is not None:
            errors.append({"source": source["id"], "error": str(last_error)})

    if not clips:
        (out_dir / "errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("No clips rendered.")
        return 1

    if len(clips) < len(selected):
        (out_dir / "errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Incomplete render: {len(clips)}/{len(selected)} clips rendered.")
        return 1

    video = xfade_clips(clips, out_dir, args.duration, args.transition)
    cover = make_cover(video, out_dir)
    rendered_ids = {clip.stem.removeprefix("clip_").split("_", 1)[1] for clip in clips}
    rendered_sources = [source for source in selected if source["id"] in rendered_ids]
    write_manifest(out_dir, rendered_sources, video, cover, args.duration, args.transition)

    if args.record_daily_run:
        record_file = append_run(
            slot=args.slot,
            source_ids=[source["id"] for source in rendered_sources],
            video=str(video),
            cover=str(cover),
            manifest=str(out_dir / "manifest.json"),
            date_key=record_date,
        )
        print(f"Daily record: {record_file}")

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
