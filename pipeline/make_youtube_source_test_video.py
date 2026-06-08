# -*- coding: utf-8 -*-
"""Build an internal Today on Earth test video from every YouTube source.

This script is for source evaluation. It reuses the user's logged-in Chrome
session, records the visible YouTube player area, applies the locked Today on
Earth overlay, and combines all usable sources into one review render.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes
import gc
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image

from make_full_video import DEFAULT_INTRO, combine_intro
from make_sample_video import FFMPEG, get_weather, local_time, make_cover, run
from render_top_overlay import render_overlay


CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_ROOT = Path(r"C:\tmp\today-on-earth-youtube-source-test")

USER32 = ctypes.windll.user32
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
VK_CONTROL = 0x11
VK_L = 0x4C
VK_V = 0x56
VK_RETURN = 0x0D
VK_F = 0x46
VK_F11 = 0x7A
VK_T = 0x54
VK_ESCAPE = 0x1B

# Current clean player crop for a maximized 1920x1080 Chrome watch page.
# It excludes Chrome UI, YouTube chrome, right live chat, title, and controls.
PLAYER_CROP = {"x": 87, "y": 245, "w": 1250, "h": 704}
LARGE_FULLSCREEN_CROP = {"x": 50, "y": 57, "w": 1816, "h": 1022}
HUMAN_FULLSCREEN_CROP = {"x": 0, "y": 0, "w": 1920, "h": 1080}
OPENCLI = shutil.which("opencli")
OPENCLI_SESSION = "toe-video"


SOURCE_META: dict[str, dict] = {
    "WJvIErIyWNc": {
        "city": "Seoul Han River",
        "city_cn": "首尔汉江",
        "country": "South Korea",
        "country_cn": "韩国",
        "latitude": 37.5326,
        "longitude": 127.0246,
        "timezone": "Asia/Seoul",
        "rating": "gold",
    },
    "P28De9FyTrM": {
        "city": "Seoul Namsan",
        "city_cn": "首尔南山",
        "country": "South Korea",
        "country_cn": "韩国",
        "latitude": 37.5512,
        "longitude": 126.9882,
        "timezone": "Asia/Seoul",
        "rating": "gold",
    },
    "VhRcNCbguWU": {
        "city": "Tokyo Shinjuku",
        "city_cn": "东京新宿",
        "country": "Japan",
        "country_cn": "日本",
        "latitude": 35.6938,
        "longitude": 139.7034,
        "timezone": "Asia/Tokyo",
        "rating": "usable",
        "edge_crop": 0.08,
        "crop_left": 0.02,
        "crop_right": 0.22,
        "crop_top": 0.10,
        "crop_bottom": 0.14,
    },
    "UdUEnefo_xQ": {
        "city": "Sydney",
        "city_cn": "悉尼",
        "country": "Australia",
        "country_cn": "澳大利亚",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "timezone": "Australia/Sydney",
        "rating": "gold",
    },
    "DEycz2Ufv98": {
        "city": "Tokyo",
        "city_cn": "东京",
        "country": "Japan",
        "country_cn": "日本",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "timezone": "Asia/Tokyo",
        "rating": "gold",
        "edge_crop": 0.08,
    },
    "VT_5rMtTS3s": {
        "city": "Shinjuku Kabukicho",
        "city_cn": "新宿歌舞伎町",
        "country": "Japan",
        "country_cn": "日本",
        "latitude": 35.6947,
        "longitude": 139.7038,
        "timezone": "Asia/Tokyo",
        "rating": "usable",
        "edge_crop": 0.12,
    },
    "aaJT8y3zfWs": {
        "city": "Venice Grand Canal",
        "city_cn": "威尼斯大运河",
        "country": "Italy",
        "country_cn": "意大利",
        "latitude": 45.4408,
        "longitude": 12.3155,
        "timezone": "Europe/Rome",
        "rating": "usable",
        "edge_crop": 0.12,
    },
    "XX7Gpd9T8Zo": {
        "city": "Las Vegas Strip",
        "city_cn": "拉斯维加斯大道",
        "country": "United States",
        "country_cn": "美国",
        "latitude": 36.1147,
        "longitude": -115.1728,
        "timezone": "America/Los_Angeles",
        "rating": "usable",
        "edge_crop": 0.08,
    },
    "-UBfUOjHymU": {
        "city": "Busan Haeundae",
        "city_cn": "釜山海云台",
        "country": "South Korea",
        "country_cn": "韩国",
        "latitude": 35.1587,
        "longitude": 129.1604,
        "timezone": "Asia/Seoul",
        "rating": "usable",
        "edge_crop": 0.08,
    },
    "iZt9BDWbEDU": {
        "city": "Sapporo",
        "city_cn": "札幌",
        "country": "Japan",
        "country_cn": "日本",
        "latitude": 43.0618,
        "longitude": 141.3545,
        "timezone": "Asia/Tokyo",
        "rating": "backup",
        "edge_crop": 0.1,
    },
    "nu6NE55_X7A": {
        "city": "Tokyo Tower",
        "city_cn": "东京塔",
        "country": "Japan",
        "country_cn": "日本",
        "latitude": 35.6586,
        "longitude": 139.7454,
        "timezone": "Asia/Tokyo",
        "rating": "usable",
        "edge_crop": 0.08,
    },
    "O0UGT7AT3aw": {
        "city": "Chicago Skydeck",
        "city_cn": "芝加哥观景台",
        "country": "United States",
        "country_cn": "美国",
        "latitude": 41.8789,
        "longitude": -87.6359,
        "timezone": "America/Chicago",
        "rating": "gold",
    },
    "R2jNOtYEwdI": {
        "city": "New York Upper East Side",
        "city_cn": "纽约上东区",
        "country": "United States",
        "country_cn": "美国",
        "latitude": 40.7736,
        "longitude": -73.9566,
        "timezone": "America/New_York",
        "rating": "backup",
        "edge_crop": 0.08,
    },
    "jQNVnjtLoQ8": {
        "city": "Makkah",
        "city_cn": "麦加",
        "country": "Saudi Arabia",
        "country_cn": "沙特阿拉伯",
        "latitude": 21.3891,
        "longitude": 39.8579,
        "timezone": "Asia/Riyadh",
        "rating": "heavy_overlay",
        "edge_crop": 0.14,
    },
    "h8glPXsnezU": {
        "city": "Oxford Broad Street",
        "city_cn": "牛津布罗德街",
        "country": "United Kingdom",
        "country_cn": "英国",
        "latitude": 51.7548,
        "longitude": -1.2544,
        "timezone": "Europe/London",
        "rating": "gold",
    },
    "rxyNjFKwzJA": {
        "city": "Vancouver",
        "city_cn": "温哥华",
        "country": "Canada",
        "country_cn": "加拿大",
        "latitude": 49.2827,
        "longitude": -123.1207,
        "timezone": "America/Vancouver",
        "rating": "gold",
    },
    "avCLVuQuiHM": {
        "city": "Hong Kong",
        "city_cn": "香港",
        "country": "China",
        "country_cn": "中国",
        "latitude": 22.3193,
        "longitude": 114.1694,
        "timezone": "Asia/Hong_Kong",
        "rating": "heavy_overlay",
        "edge_crop": 0.14,
    },
    "z-jYdOIKcTQ": {
        "city": "Times Square",
        "city_cn": "纽约时代广场",
        "country": "United States",
        "country_cn": "美国",
        "latitude": 40.758,
        "longitude": -73.9855,
        "timezone": "America/New_York",
        "rating": "usable",
        "edge_crop": 0.08,
    },
    "qx7gry390YA": {
        "city": "Niagara Falls",
        "city_cn": "尼亚加拉瀑布",
        "country": "Canada",
        "country_cn": "加拿大",
        "latitude": 43.0896,
        "longitude": -79.0849,
        "timezone": "America/Toronto",
        "rating": "gold",
    },
    "7i8ARjIeM2k": {
        "city": "Coral City",
        "city_cn": "珊瑚城",
        "country": "United States",
        "country_cn": "美国",
        "latitude": 25.7617,
        "longitude": -80.1918,
        "timezone": "America/New_York",
        "rating": "usable",
    },
    "z_fY1pj1VBw": {
        "city": "Taipei Xiangshan",
        "city_cn": "台北象山",
        "country": "Taiwan",
        "country_cn": "中国台湾",
        "latitude": 25.033,
        "longitude": 121.5654,
        "timezone": "Asia/Taipei",
        "rating": "usable",
    },
}


def set_clipboard(text: str) -> None:
    escaped = text.replace("'", "''")
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{escaped}'"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def key_down(vk: int) -> None:
    USER32.keybd_event(vk, 0, 0, 0)


def key_up(vk: int) -> None:
    USER32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def hotkey(*keys: int) -> None:
    for key in keys:
        key_down(key)
    time.sleep(0.08)
    for key in reversed(keys):
        key_up(key)
    time.sleep(0.25)


def press(vk: int) -> None:
    key_down(vk)
    time.sleep(0.05)
    key_up(vk)
    time.sleep(0.25)


def click(x: int, y: int) -> None:
    USER32.SetCursorPos(x, y)
    time.sleep(0.12)
    USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def visible_titled_windows() -> list[tuple[int, str]]:
    hwnds: list[tuple[int, str]] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def enum_proc(hwnd, _) -> bool:
        if USER32.IsWindowVisible(hwnd):
            length = USER32.GetWindowTextLengthW(hwnd)
            if length > 0:
                title = ctypes.create_unicode_buffer(length + 1)
                USER32.GetWindowTextW(hwnd, title, length + 1)
                hwnds.append((hwnd, title.value))
        return True

    USER32.EnumWindows(enum_proc, 0)
    return hwnds


def chrome_windows() -> list[tuple[int, str]]:
    return [
        (hwnd, title)
        for hwnd, title in visible_titled_windows()
        if "Chrome" in title or "YouTube" in title
    ]


def foreground_chrome(maximize: bool = True) -> tuple[int, str]:
    windows = chrome_windows()
    if not windows:
        subprocess.Popen([CHROME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        windows = chrome_windows()
    if not windows:
        raise RuntimeError("No visible Chrome window found.")

    hwnd, title = windows[0]
    USER32.ShowWindow(hwnd, SW_RESTORE)
    if maximize:
        USER32.ShowWindow(hwnd, SW_MAXIMIZE)
    USER32.SetForegroundWindow(hwnd)
    time.sleep(0.8)
    return hwnd, title


def focus_chrome() -> tuple[int, str]:
    windows = chrome_windows()
    if not windows:
        raise RuntimeError("No visible Chrome window found.")
    hwnd, title = windows[0]
    USER32.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    return hwnd, title


def minimize_non_chrome_windows() -> None:
    for hwnd, title in visible_titled_windows():
        normalized = title.lower()
        if "chrome" in normalized or "youtube" in normalized:
            continue
        if normalized in {"program manager", "windows input experience"}:
            continue
        USER32.ShowWindow(hwnd, SW_MINIMIZE)
        time.sleep(0.05)


def parse_source_file(path: Path) -> tuple[list[dict], list[str]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    sources: list[dict] = []
    channel_pages: list[str] = []
    pending_label = ""
    seen: set[str] = set()

    for index, line in enumerate(lines):
        if not line:
            continue
        if not line.startswith("http"):
            pending_label = line
            continue
        if "@earthcam/streams" in line:
            channel_pages.append(line)
            pending_label = ""
            continue

        match = re.search(r"(?:v=|youtu\.be/)([-_A-Za-z0-9]{11})", line)
        if not match:
            pending_label = ""
            continue
        video_id = match.group(1)
        if video_id in seen:
            pending_label = ""
            continue
        seen.add(video_id)

        meta = SOURCE_META.get(video_id, {})
        source = {
            "id": f"youtube_{video_id}",
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}&autoplay=1&mute=1",
            "original_url": line,
            "label": pending_label,
            "order": len(sources) + 1,
            "provider": "YouTube",
            "rights_status": "permission_needed",
            "usage_mode": "internal_demo",
            "edge_crop": 0.06,
            **meta,
        }
        source.setdefault("city", pending_label or video_id)
        source.setdefault("city_cn", source["city"])
        source.setdefault("country", "Unknown")
        source.setdefault("country_cn", "未知")
        source.setdefault("timezone", "UTC")
        sources.append(source)
        pending_label = ""

    return sources, channel_pages


def open_source(source: dict, wait_seconds: float) -> None:
    subprocess.Popen([CHROME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.6)
    foreground_chrome()
    set_clipboard(source["url"])
    hotkey(VK_CONTROL, VK_L)
    hotkey(VK_CONTROL, VK_V)
    press(VK_RETURN)
    time.sleep(wait_seconds)
    # Move the mouse outside the capture crop so YouTube controls fade away.
    USER32.SetCursorPos(1820, 190)
    time.sleep(3.5)


def run_opencli_browser(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    if not OPENCLI:
        raise RuntimeError("opencli is required for human-fullscreen capture.")
    result = run([OPENCLI, "browser", OPENCLI_SESSION, *args], timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip()[-1200:])
    return result


def try_run_opencli_browser(*args: str, timeout: int = 120) -> None:
    try:
        run_opencli_browser(*args, timeout=timeout)
    except (RuntimeError, subprocess.TimeoutExpired):
        pass


def parse_opencli_object(output: str) -> dict:
    text = output.strip()
    if not text:
        return {}
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return {}
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
        return value if isinstance(value, dict) else {}


def needs_f11_fullscreen(viewport: dict) -> bool:
    inner_h = int(viewport.get("innerHeight") or 0)
    screen_h = int(viewport.get("screenHeight") or 1080)
    return screen_h >= 1000 and inner_h < 980


def prepare_recording_desktop(viewport: dict, allow_f11: bool = True) -> None:
    minimize_non_chrome_windows()
    if allow_f11 and needs_f11_fullscreen(viewport):
        foreground_chrome(maximize=True)
        press(VK_F11)
        time.sleep(2.0)
    else:
        focus_chrome()
    close_chrome_debug_bar()
    USER32.SetCursorPos(1910, 1070)
    time.sleep(1.4)


def capture_precheck(out_dir: Path, index: int, source: dict, crop: dict) -> Path:
    precheck = out_dir / f"precheck_{index:02d}_{source['video_id']}.jpg"
    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "gdigrab",
        "-draw_mouse",
        "0",
        "-framerate",
        "1",
        "-offset_x",
        str(crop["x"]),
        "-offset_y",
        str(crop["y"]),
        "-video_size",
        f"{crop['w']}x{crop['h']}",
        "-i",
        "desktop",
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(precheck),
    ]
    subprocess.run(cmd, check=True, timeout=30)
    return precheck


def close_chrome_debug_bar() -> None:
    # Chrome shows "OpenCLI started debugging this browser" while the bridge is
    # attached. After unbind, close the browser-level infobar before recording.
    for x, y in [(1889, 28), (1892, 27), (1886, 26)]:
        click(x, y)
        time.sleep(0.35)


def human_fullscreen_script() -> str:
    return (
        "(() => {"
        "const p=document.querySelector('#movie_player');"
        "try { p?.setPlaybackQualityRange?.('hd1080'); p?.setPlaybackQuality?.('hd1080'); } catch(e) {}"
        "document.querySelectorAll('ytd-live-chat-frame,#chat,#secondary,#related,#masthead,"
        "#below,tp-yt-paper-dialog,ytd-popup-container,.ytp-ce-element,.ytp-cards-teaser,"
        ".ytp-chrome-top,.ytp-chrome-bottom').forEach(e=>e.remove());"
        "document.documentElement.style.cssText='margin:0!important;overflow:hidden!important;background:#000!important;width:100%!important;height:100%!important';"
        "document.body.style.cssText='margin:0!important;overflow:hidden!important;background:#000!important;width:100%!important;height:100%!important';"
        "let host=document.getElementById('toe-video-host');"
        "if(!host){host=document.createElement('div');host.id='toe-video-host';document.body.appendChild(host);}"
        "host.style.cssText='position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;"
        "background:#000!important;z-index:2147483646!important;overflow:hidden!important;display:block!important';"
        "const v=document.querySelector('video');"
        "if(v){host.appendChild(v);v.muted=true;v.play().catch(()=>{});"
        "v.removeAttribute('width');v.removeAttribute('height');"
        "v.style.cssText='position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;"
        "max-width:none!important;max-height:none!important;min-width:100vw!important;min-height:100vh!important;"
        "object-fit:cover!important;background:#000!important;z-index:2147483647!important;pointer-events:none!important;display:block!important';}"
        "const old=document.getElementById('toe-video-style'); old?.remove();"
        "const s=document.createElement('style');s.id='toe-video-style';"
        "s.textContent='*{cursor:none!important} html,body,ytd-app,#content,#page-manager,ytd-watch-flexy{background:#000!important;overflow:hidden!important;width:100%!important;height:100%!important} video{width:100vw!important;height:100vh!important;object-fit:cover!important}';"
        "document.head.appendChild(s);"
        "return {ok:!!v, quality:p?.getPlaybackQuality?.(), w:v?.videoWidth, h:v?.videoHeight,"
        "clientWidth:v?.clientWidth,clientHeight:v?.clientHeight,"
        "innerWidth:window.innerWidth,innerHeight:window.innerHeight,"
        "outerWidth:window.outerWidth,outerHeight:window.outerHeight,"
        "screenWidth:screen.width,screenHeight:screen.height};"
        "})()"
    )


def prepare_human_fullscreen(source: dict, out_dir: Path, index: int, wait_seconds: float) -> Path:
    watch_url = f"https://www.youtube.com/watch?v={source['video_id']}"
    try_run_opencli_browser("unbind", timeout=15)
    minimize_non_chrome_windows()
    foreground_chrome(maximize=True)
    set_clipboard(watch_url)
    hotkey(VK_CONTROL, VK_L)
    hotkey(VK_CONTROL, VK_V)
    press(VK_RETURN)
    time.sleep(wait_seconds)
    run_opencli_browser("bind", timeout=60)
    run_opencli_browser("wait", "time", "1.5", timeout=30)
    script = human_fullscreen_script()
    result = run_opencli_browser("eval", script, timeout=60)
    viewport = parse_opencli_object(result.stdout)
    print(f"  opencli: {result.stdout.strip()[:260]}")
    if needs_f11_fullscreen(viewport):
        minimize_non_chrome_windows()
        foreground_chrome(maximize=True)
        press(VK_F11)
        time.sleep(2.2)
        result = run_opencli_browser("eval", script, timeout=60)
        viewport = parse_opencli_object(result.stdout)
        print(f"  opencli fullscreen: {result.stdout.strip()[:260]}")
    try_run_opencli_browser("unbind", timeout=30)
    prepare_recording_desktop(viewport, allow_f11=False)
    return capture_precheck(out_dir, index, source, HUMAN_FULLSCREEN_CROP)


def record_source(
    source: dict,
    index: int,
    out_dir: Path,
    duration: float,
    wait_seconds: float,
    capture_mode: str = "small-player",
) -> Path:
    raw = out_dir / f"raw_{index:02d}_{source['video_id']}.mp4"
    if raw.exists() and raw.stat().st_size > 0:
        return raw

    source["_capture_mode"] = capture_mode
    if capture_mode == "human-fullscreen":
        precheck = prepare_human_fullscreen(source, out_dir, index, wait_seconds)
        print(f"  precheck: {precheck.name}")
        crop = HUMAN_FULLSCREEN_CROP
    else:
        open_source(source, wait_seconds)

    if capture_mode == "large-fullscreen":
        click(720, 520)
        time.sleep(0.4)
        press(VK_F)
        time.sleep(5)
        USER32.SetCursorPos(1910, 20)
        time.sleep(2)
        crop = LARGE_FULLSCREEN_CROP
    elif capture_mode != "human-fullscreen":
        crop = PLAYER_CROP

    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "gdigrab",
        "-draw_mouse",
        "0",
        "-framerate",
        "30",
        "-offset_x",
        str(crop["x"]),
        "-offset_y",
        str(crop["y"]),
        "-video_size",
        f"{crop['w']}x{crop['h']}",
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
    try:
        subprocess.run(cmd, check=True, timeout=max(60, round(duration + 30)))
    finally:
        if capture_mode == "large-fullscreen":
            press(VK_ESCAPE)
        elif capture_mode == "human-fullscreen":
            press(VK_F11)
            time.sleep(1.2)
    return raw


def render_source_clip(
    raw: Path,
    source: dict,
    index: int,
    out_dir: Path,
    duration: float,
    overlay_delay: float,
) -> Path:
    clip = out_dir / f"clip_{index:02d}_{source['video_id']}.mp4"
    if clip.exists() and clip.stat().st_size > 0:
        return clip

    weather = get_weather(source)
    rendered_local_time = local_time(source)
    source["_render_weather"] = weather
    source["_render_local_time"] = rendered_local_time

    overlay = out_dir / f"overlay_{index:02d}_{source['video_id']}.png"
    city_label = f"{source['city']} {source['city_cn']}"
    country_label = f"{source['country']} {source['country_cn']}"
    render_overlay(
        overlay,
        city_label=city_label,
        country_label=country_label,
        temp_c=weather.get("temp_c", 17),
        wind_kmh=weather.get("wind_kmh", 10),
        humidity=weather.get("humidity", 73),
        local_time=rendered_local_time,
    )

    edge = float(source.get("edge_crop", 0.06))
    if source.get("_capture_mode") == "human-fullscreen":
        edge = max(edge, 0.085)
    crop_left = float(source.get("crop_left", edge))
    crop_right = float(source.get("crop_right", edge))
    crop_top = float(source.get("crop_top", edge))
    crop_bottom = float(source.get("crop_bottom", edge))
    crop_expr = (
        f"crop=w=iw*{1 - crop_left - crop_right:.4f}:h=ih*{1 - crop_top - crop_bottom:.4f}:"
        f"x=iw*{crop_left:.4f}:y=ih*{crop_top:.4f}"
    )
    base_filters = [
        crop_expr,
        "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos",
        "crop=1920:1080",
        "fps=30",
        "eq=contrast=1.045:brightness=0.012:saturation=1.045",
        "hqdn3d=luma_spatial=1.3:chroma_spatial=1.8:luma_tmp=2",
        "unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=0.32",
    ]
    overlay_in_duration = 1.15
    overlay_in_end = overlay_delay + overlay_in_duration
    overlay_fade_out = max(duration - 1.05, 1.35)
    filter_complex = (
        f"[0:v]{','.join(base_filters)}[base];"
        "[1:v]format=rgba,"
        f"fade=t=in:st={overlay_delay:.2f}:d={overlay_in_duration:.2f}:alpha=1,"
        f"fade=t=out:st={overlay_fade_out:.2f}:d=0.50:alpha=1[ov];"
        f"[base][ov]overlay=x=0:y='if(lt(t,{overlay_in_end:.2f}),"
        f"-8+8*pow(min(max((t-{overlay_delay:.2f})/{overlay_in_duration:.2f}\\,0)\\,1)\\,0.55),0)':format=auto[v]"
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
        str(clip),
    ]
    subprocess.run(cmd, check=True, timeout=max(90, round(duration * 20)))
    return clip


def xfade_pairwise(clips: list[Path], out_dir: Path, clip_duration: float, transition: float) -> Path:
    if not clips:
        raise ValueError("No clips to combine.")
    if len(clips) == 1:
        output = out_dir / "today-on-earth-youtube-source-test-live.mp4"
        shutil.copy2(clips[0], output)
        return output

    previous = clips[0]
    current_duration = clip_duration
    for index, clip in enumerate(clips[1:], start=2):
        output = out_dir / f"xfade_step_{index:02d}.mp4"
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

    live = out_dir / "today-on-earth-youtube-source-test-live.mp4"
    shutil.copy2(previous, live)
    return live


def make_timeline(video: Path, out_dir: Path) -> Path:
    timeline = out_dir / "timeline-4x5.jpg"
    vf = "fps=1/6,scale=384:216,tile=4x5"
    result = run(
        [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vf",
            vf,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(timeline),
        ],
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-1000:])
    return timeline


def write_manifest(
    *,
    out_dir: Path,
    final_video: Path,
    live_video: Path,
    cover: Path,
    timeline: Path,
    rendered_sources: list[dict],
    failed_sources: list[dict],
    channel_pages: list[str],
    duration: float,
    transition: float,
    intro: Path,
) -> Path:
    live_duration = len(rendered_sources) * duration
    if len(rendered_sources) > 1:
        live_duration -= (len(rendered_sources) - 1) * transition
    manifest = {
        "project": "Today on Earth",
        "render_type": "youtube_all_sources_internal_test",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "rights_note": "Internal visual test only. YouTube sources are not cleared for public/commercial use.",
        "watermark_cleanup": "Browser/player UI is excluded by crop. Burned-in corner/logo/URL marks are reduced with edge crop and HD normalization.",
        "player_crop": PLAYER_CROP,
        "clip_duration_seconds": duration,
        "transition_duration_seconds": transition,
        "estimated_live_duration_seconds": round(live_duration, 2),
        "intro": str(intro),
        "live_video": str(live_video),
        "full_video": str(final_video),
        "cover": str(cover),
        "timeline": str(timeline),
        "channel_pages_not_expanded": channel_pages,
        "sources": [
            {
                "id": s["id"],
                "video_id": s["video_id"],
                "city": s["city"],
                "city_cn": s["city_cn"],
                "country": s["country"],
                "country_cn": s["country_cn"],
                "url": s["original_url"],
                "provider": s["provider"],
                "rating": s.get("rating"),
                "edge_crop": s.get("edge_crop"),
                "rights_status": s.get("rights_status"),
                "usage_mode": s.get("usage_mode"),
                "timezone": s.get("timezone"),
                "local_time": s.get("_render_local_time"),
                "weather": s.get("_render_weather"),
            }
            for s in rendered_sources
        ],
        "failed_sources": failed_sources,
    }
    manifest_path = out_dir / "manifest.youtube-source-test.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", type=Path, default=Path(r"C:\Users\Administrator\Desktop\today-on-earth\镜头源.txt"))
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--transition", type=float, default=0.55)
    parser.add_argument("--first-overlay-delay", type=float, default=1.05)
    parser.add_argument("--wait", type=float, default=18.0)
    parser.add_argument(
        "--capture-mode",
        choices=["small-player", "large-fullscreen", "human-fullscreen"],
        default="small-player",
    )
    parser.add_argument("--intro", type=Path, default=DEFAULT_INTRO)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--only-ids", default="")
    parser.add_argument("--max-sources", type=int, default=None)
    parser.add_argument("--skip-intro", action="store_true")
    args = parser.parse_args()

    sources, channel_pages = parse_source_file(args.source_file)
    only_ids = {item.strip() for item in args.only_ids.split(",") if item.strip()}
    if only_ids:
        sources = [source for source in sources if source["video_id"] in only_ids]
    if args.max_sources:
        sources = sources[: args.max_sources]
    if not sources:
        raise SystemExit("No YouTube video sources found.")

    out_dir = args.output_dir or OUTPUT_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output: {out_dir}")
    print(f"Source file: {args.source_file}")
    print(f"Plan: {len(sources)} sources x {args.duration}s, transition {args.transition:.2f}s")
    print(f"Capture mode: {args.capture_mode}")
    print("Sources:")
    for source in sources:
        print(
            f"  {source['order']:02d}. {source['city']} {source['city_cn']}, "
            f"{source['country']} {source['country_cn']} | {source['video_id']}"
        )

    clips: list[Path] = []
    rendered_sources: list[dict] = []
    failed_sources: list[dict] = []

    for index, source in enumerate(sources, start=1):
        print(f"\n[{index}/{len(sources)}] {source['city']} {source['city_cn']} ({source['video_id']})")
        try:
            raw = record_source(source, index, out_dir, args.duration + 0.25, args.wait, args.capture_mode)
            overlay_delay = args.first_overlay_delay if index == 1 else 0.25
            clip = render_source_clip(raw, source, index, out_dir, args.duration, overlay_delay)
            clips.append(clip)
            rendered_sources.append(source)
            print(f"  ok: {clip.name}")
        except Exception as exc:
            failed_sources.append(
                {
                    "video_id": source["video_id"],
                    "city": source.get("city"),
                    "city_cn": source.get("city_cn"),
                    "url": source.get("original_url"),
                    "error": str(exc),
                }
            )
            print(f"  failed: {exc}")
        gc.collect()

    if not clips:
        errors = out_dir / "errors.json"
        errors.write_text(json.dumps(failed_sources, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"No clips rendered. Errors: {errors}")
        return 1

    live_video = xfade_pairwise(clips, out_dir, args.duration, args.transition)
    if args.skip_intro:
        final_video = out_dir / "today-on-earth-youtube-source-test-live-only.mp4"
        shutil.copy2(live_video, final_video)
    else:
        final_video = out_dir / f"today-on-earth-youtube-source-test-{len(rendered_sources)}-sources.mp4"
        live_duration = len(rendered_sources) * args.duration
        if len(rendered_sources) > 1:
            live_duration -= (len(rendered_sources) - 1) * args.transition
        combine_intro(args.intro, live_video, final_video, live_duration)

    cover = make_cover(final_video, out_dir)
    timeline = make_timeline(final_video, out_dir)
    manifest = write_manifest(
        out_dir=out_dir,
        final_video=final_video,
        live_video=live_video,
        cover=cover,
        timeline=timeline,
        rendered_sources=rendered_sources,
        failed_sources=failed_sources,
        channel_pages=channel_pages,
        duration=args.duration,
        transition=args.transition,
        intro=args.intro,
    )

    print("\nDone.")
    print(f"Rendered sources: {len(rendered_sources)}/{len(sources)}")
    print(f"Full video: {final_video}")
    print(f"Manifest: {manifest}")
    print(f"Timeline: {timeline}")
    if failed_sources:
        print(f"Failures: {len(failed_sources)}")
    return 0 if rendered_sources else 1


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
