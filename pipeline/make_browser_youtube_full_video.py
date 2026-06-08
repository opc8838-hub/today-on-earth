"""Build a Today on Earth test video from YouTube streams playing in real Chrome.

This is a fallback path for YouTube live sources when yt-dlp is blocked by bot
checks. It records the visible Chrome player area, then applies the same
Today on Earth overlay and intro composition rules as the normal factory.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes
import gc
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from daily_record import append_run, today_key
from make_full_video import DEFAULT_INTRO
from make_sample_video import FFMPEG, get_weather, local_time, make_cover
from render_top_overlay import render_overlay


CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WORK_ROOT = Path(r"C:\tmp\today-on-earth-browser-youtube")

USER32 = ctypes.windll.user32
SW_MAXIMIZE = 3
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_L = 0x4C
VK_V = 0x56
VK_RETURN = 0x0D


SOURCES = [
    {
        "id": "youtube_las_vegas_strip",
        "url": "https://www.youtube.com/watch?v=XX7Gpd9T8Zo",
        "city": "Las Vegas Strip",
        "city_cn": "拉斯维加斯大道",
        "country": "United States",
        "country_cn": "美国",
        "latitude": 36.1147,
        "longitude": -115.1728,
        "timezone": "America/Los_Angeles",
        "weather": {"temp_c": 28, "wind_kmh": 12, "humidity": 28},
    },
    {
        "id": "youtube_seoul_namsan",
        "url": "https://www.youtube.com/watch?v=P28De9FyTrM",
        "city": "Seoul Namsan",
        "city_cn": "首尔南山",
        "country": "South Korea",
        "country_cn": "韩国",
        "latitude": 37.5512,
        "longitude": 126.9882,
        "timezone": "Asia/Seoul",
        "weather": {"temp_c": 22, "wind_kmh": 8, "humidity": 65},
    },
    {
        "id": "youtube_tokyo_live_4k",
        "url": "https://www.youtube.com/watch?v=DEycz2Ufv98",
        "city": "Tokyo",
        "city_cn": "东京",
        "country": "Japan",
        "country_cn": "日本",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "timezone": "Asia/Tokyo",
        "weather": {"temp_c": 23, "wind_kmh": 9, "humidity": 68},
    },
    {
        "id": "youtube_chicago_skydeck",
        "url": "https://www.youtube.com/watch?v=O0UGT7AT3aw",
        "city": "Chicago",
        "city_cn": "芝加哥",
        "country": "United States",
        "country_cn": "美国",
        "latitude": 41.8781,
        "longitude": -87.6298,
        "timezone": "America/Chicago",
        "weather": {"temp_c": 21, "wind_kmh": 12, "humidity": 58},
    },
    {
        "id": "youtube_oxford_broad_street",
        "url": "https://www.youtube.com/watch?v=h8glPXsnezU",
        "city": "Oxford",
        "city_cn": "牛津",
        "country": "United Kingdom",
        "country_cn": "英国",
        "latitude": 51.7520,
        "longitude": -1.2577,
        "timezone": "Europe/London",
        "weather": {"temp_c": 16, "wind_kmh": 10, "humidity": 71},
    },
    {
        "id": "youtube_busan_haeundae",
        "url": "https://www.youtube.com/watch?v=-UBfUOjHymU",
        "city": "Busan Haeundae",
        "city_cn": "釜山海云台",
        "country": "South Korea",
        "country_cn": "韩国",
        "latitude": 35.1587,
        "longitude": 129.1604,
        "timezone": "Asia/Seoul",
        "weather": {"temp_c": 22, "wind_kmh": 11, "humidity": 68},
    },
    {
        "id": "youtube_niagara_falls",
        "url": "https://www.youtube.com/watch?v=qx7gry390YA",
        "city": "Niagara Falls",
        "city_cn": "尼亚加拉瀑布",
        "country": "Canada",
        "country_cn": "加拿大",
        "latitude": 43.0962,
        "longitude": -79.0377,
        "timezone": "America/Toronto",
        "weather": {"temp_c": 18, "wind_kmh": 11, "humidity": 70},
    },
]


def key_down(vk: int) -> None:
    USER32.keybd_event(vk, 0, 0, 0)


def key_up(vk: int) -> None:
    USER32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def hotkey(*keys: int) -> None:
    for key in keys:
        key_down(key)
    time.sleep(0.1)
    for key in reversed(keys):
        key_up(key)
    time.sleep(0.3)


def press(vk: int) -> None:
    key_down(vk)
    time.sleep(0.05)
    key_up(vk)
    time.sleep(0.3)


def click(x: int, y: int) -> None:
    USER32.SetCursorPos(x, y)
    time.sleep(0.15)
    USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def foreground_chrome() -> tuple[int, int, int, int]:
    hwnds: list[int] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def enum_proc(hwnd, _) -> bool:
        if USER32.IsWindowVisible(hwnd):
            length = USER32.GetWindowTextLengthW(hwnd)
            if length > 0:
                title = ctypes.create_unicode_buffer(length + 1)
                USER32.GetWindowTextW(hwnd, title, length + 1)
                if "Chrome" in title.value:
                    hwnds.append(hwnd)
        return True

    USER32.EnumWindows(enum_proc, 0)
    if not hwnds:
        raise RuntimeError("No visible Chrome window found")
    hwnd = hwnds[0]
    USER32.ShowWindow(hwnd, SW_MAXIMIZE)
    USER32.SetForegroundWindow(hwnd)
    time.sleep(1)
    rect = ctypes.wintypes.RECT()
    USER32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def set_clipboard(text: str) -> None:
    escaped = text.replace("'", "''")
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{escaped}'"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def open_source(source: dict, wait: int) -> tuple[int, int, int, int]:
    subprocess.Popen([CHROME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    left, top, right, bottom = foreground_chrome()
    set_clipboard(source["url"])
    hotkey(VK_CONTROL, VK_L)
    hotkey(VK_CONTROL, VK_V)
    press(VK_RETURN)
    time.sleep(wait)
    # Click once only to dismiss focus overlays; the video usually autoplays in
    # the user's logged-in browser. Wait for controls to fade before recording.
    click(left + (right - left) // 2, top + (bottom - top) // 2)
    time.sleep(4)
    return left, top, right, bottom


def record_player(source: dict, out_dir: Path, index: int, duration: float, wait: int) -> Path:
    raw = out_dir / f"raw_{index:02d}_{source['id']}.mp4"
    if raw.exists() and raw.stat().st_size > 0:
        return raw
    left, top, _, _ = open_source(source, wait)
    capture_x = left + 44
    capture_y = top + 196
    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "gdigrab",
        "-framerate",
        "30",
        "-offset_x",
        str(capture_x),
        "-offset_y",
        str(capture_y),
        "-video_size",
        "1350x760",
        "-i",
        "desktop",
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        str(raw),
    ]
    subprocess.run(cmd, check=True, timeout=max(60, duration + 20))
    return raw


def render_clip(raw: Path, source: dict, out_dir: Path, index: int, duration: float, overlay_delay: float) -> Path:
    out = out_dir / f"clip_{index:02d}_{source['id']}.mp4"
    weather = get_weather(source)
    source["_render_weather"] = weather
    source["_render_local_time"] = local_time(source)

    if out.exists() and out.stat().st_size > 0:
        return out

    overlay = out_dir / f"overlay_{index:02d}_{source['id']}.png"

    render_overlay(
        overlay,
        city_label=f"{source['city']} {source['city_cn']}",
        country_label=f"{source['country']} {source['country_cn']}",
        temp_c=weather.get("temp_c", 18),
        wind_kmh=weather.get("wind_kmh", 10),
        humidity=weather.get("humidity", 70),
        local_time=source["_render_local_time"],
    )

    overlay_fade_out = max(duration - 1.05, 1.35)
    overlay_in_duration = 1.10
    overlay_in_end = overlay_delay + overlay_in_duration
    base_filters = [
        "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos",
        "crop=1920:1080",
        "fps=30",
        "eq=contrast=1.04:brightness=0.015:saturation=1.04",
        "hqdn3d=luma_spatial=1.5:chroma_spatial=2:luma_tmp=2",
        "unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=0.35",
    ]
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
        "-i",
        str(raw),
        "-loop",
        "1",
        "-i",
        str(overlay),
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
        str(out),
    ]
    subprocess.run(cmd, check=True, timeout=max(90, duration * 20))
    return out


def xfade_pairwise(clips: list[Path], out_dir: Path, clip_duration: float, transition: float) -> Path:
    if not clips:
        raise ValueError("No clips to crossfade")

    previous = clips[0]
    current_duration = clip_duration
    for index, clip in enumerate(clips[1:], 2):
        output = out_dir / f"xfade_step_{index:02d}.mp4"
        if output.exists() and output.stat().st_size > 0:
            previous = output
            current_duration += clip_duration - transition
            continue

        offset = max(current_duration - transition, 0.0)
        filter_complex = (
            "[0:v]setpts=PTS-STARTPTS,format=yuv420p[v0];"
            "[1:v]setpts=PTS-STARTPTS,format=yuv420p[v1];"
            f"[v0][v1]xfade=transition=fade:duration={transition:.2f}:offset={offset:.2f}[v]"
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
        ]
        subprocess.run(cmd, check=True, timeout=max(180, round(current_duration * 12)))
        previous = output
        current_duration += clip_duration - transition
        gc.collect()

    live = out_dir / "today-on-earth-browser-youtube-live.mp4"
    if not live.exists() or live.stat().st_size == 0:
        shutil.copy2(previous, live)
    return live


def combine_intro_low_memory(intro: Path, live_video: Path, output: Path, silence_seconds: float) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_size > 0:
        return output

    filter_complex = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1920:1080,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v0];"
        "[1:v]scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v1];"
        "[v0][v1]xfade=transition=fade:duration=0.70:offset=3.33[v];"
        "[0:a]atrim=0:4.034,asetpts=PTS-STARTPTS,afade=t=out:st=3.30:d=0.70[a0];"
        f"anullsrc=channel_layout=stereo:sample_rate=48000,atrim=0:{silence_seconds:.2f}[sil];"
        "[a0][sil]concat=n=2:v=0:a=1[a]"
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
        "-i",
        str(intro),
        "-i",
        str(live_video),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "[a]",
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
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True, timeout=max(240, round(silence_seconds * 12)))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--transition", type=float, default=0.55)
    parser.add_argument("--first-overlay-delay", type=float, default=1.05)
    parser.add_argument("--wait", type=int, default=25)
    parser.add_argument("--intro", type=Path, default=DEFAULT_INTRO)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--slot", choices=["morning", "afternoon", "manual"], default="manual")
    parser.add_argument("--record-date", default=today_key())
    parser.add_argument("--record-daily-run", action="store_true")
    args = parser.parse_args()

    out_dir = args.output_dir or WORK_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {out_dir}")
    print("Selected sources:")
    for source in SOURCES:
        print(f"  - {source['id']} | {source['city']} {source['city_cn']}, {source['country']} {source['country_cn']}")

    clips: list[Path] = []
    for index, source in enumerate(SOURCES, 1):
        print(f"\n[{index}/{len(SOURCES)}] Recording {source['id']}...")
        raw = record_player(source, out_dir, index, args.duration, args.wait)
        overlay_delay = args.first_overlay_delay if index == 1 else 0.25
        clip = render_clip(raw, source, out_dir, index, args.duration, overlay_delay)
        clips.append(clip)
        print(f"  ok {clip}")
        gc.collect()

    live_video = xfade_pairwise(clips, out_dir, args.duration, args.transition)
    final = out_dir / "today-on-earth-browser-youtube-7-regions.mp4"
    combine_intro_low_memory(args.intro, live_video, final, len(SOURCES) * args.duration - (len(SOURCES) - 1) * args.transition)
    cover = make_cover(final, out_dir)
    manifest = {
        "project": "Today on Earth",
        "render_type": "browser_youtube_fallback",
        "slot": args.slot,
        "record_date": args.record_date,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "baseline_note": "Non-repeating replacement test using real Chrome player capture because yt-dlp was blocked.",
        "duration_seconds_expected": 43,
        "final_video": str(final),
        "cover": str(cover),
        "sources": [
            {
                "id": s["id"],
                "city": s["city"],
                "city_cn": s["city_cn"],
                "country": s["country"],
                "country_cn": s["country_cn"],
                "url": s["url"],
                "weather": s.get("_render_weather"),
                "local_time": s.get("_render_local_time"),
            }
            for s in SOURCES
        ],
    }
    manifest_path = out_dir / "manifest.browser-youtube.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.record_daily_run:
        record_path = append_run(
            slot=args.slot,
            source_ids=[s["id"] for s in SOURCES],
            video=str(final),
            cover=str(cover),
            manifest=str(manifest_path),
            date_key=args.record_date,
        )
        print(f"Daily record: {record_path}")
    print(f"Full video: {final}")
    print(f"Full manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
