"""Capture real YouTube live frames from the user's visible Chrome session.

This is a review tool, not a downloader. It reuses the user's logged-in Chrome
window, opens each YouTube URL, waits for playback, and saves a player-area
screenshot so source quality is judged from real frames instead of thumbnails.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageGrab


CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER32 = ctypes.windll.user32
SW_MAXIMIZE = 3
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_L = 0x4C
VK_V = 0x56
VK_RETURN = 0x0D


def extract_sources(path: Path) -> list[dict]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    sources: list[dict] = []
    last_label = ""
    for index, line in enumerate(lines):
        if not line:
            continue
        if line.startswith("http"):
            if "@earthcam/streams" in line:
                continue
            label = last_label
            if not label and index + 1 < len(lines) and not lines[index + 1].startswith("http"):
                label = lines[index + 1].strip()
            match = re.search(r"(?:v=|youtu\.be/)([-_A-Za-z0-9]{11})", line)
            if match:
                sources.append({"label": label, "url": line, "id": match.group(1)})
            last_label = ""
        else:
            last_label = line

    deduped: list[dict] = []
    seen: set[str] = set()
    for source in sources:
        if source["id"] in seen:
            continue
        seen.add(source["id"])
        deduped.append(source)
    return deduped


def foreground_chrome() -> tuple[int, tuple[int, int, int, int]]:
    hwnds: list[int] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def enum_proc(hwnd, _) -> bool:
        if not USER32.IsWindowVisible(hwnd):
            return True
        length = USER32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
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
    return hwnd, (rect.left, rect.top, rect.right, rect.bottom)


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


def set_clipboard(text: str) -> None:
    escaped = text.replace("'", "''")
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{escaped}'"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def capture_source(source: dict, index: int, rect: tuple[int, int, int, int], out_dir: Path, wait: int) -> dict:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    set_clipboard(source["url"])
    hotkey(VK_CONTROL, VK_L)
    hotkey(VK_CONTROL, VK_V)
    press(VK_RETURN)
    time.sleep(wait)
    click(left + width // 2, top + height // 2)
    time.sleep(4)

    window = ImageGrab.grab(bbox=(left, top, right, bottom))
    window_path = out_dir / "windows" / f"{index:02d}_{source['id']}_window.png"
    crop_path = out_dir / "crops" / f"{index:02d}_{source['id']}_crop.png"
    window.save(window_path)

    crop_box = (
        max(0, 44 - left),
        max(0, 196 - top),
        min(width, 1394 - left),
        min(height, 956 - top),
    )
    crop = window.crop(crop_box)
    crop.save(crop_path)
    return {**source, "window": str(window_path), "crop": str(crop_path), "crop_size": crop.size}


def make_contact_sheet(results: list[dict], out_dir: Path) -> Path:
    thumbs = []
    for result in results:
        if "crop" not in result:
            continue
        img = Image.open(result["crop"]).convert("RGB")
        img.thumbnail((360, 205))
        canvas = Image.new("RGB", (360, 245), (12, 14, 18))
        canvas.paste(img, (0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 210), (result.get("label") or result["id"])[:42], fill=(255, 255, 255))
        draw.text((8, 228), result["id"], fill=(180, 205, 220))
        thumbs.append(canvas)

    columns = 3
    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * 360, rows * 245), (0, 0, 0))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % columns) * 360, (i // columns) * 245))
    path = out_dir / "contact-sheet.png"
    sheet.save(path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--wait", type=int, default=45)
    parser.add_argument("--only-ids", default="")
    args = parser.parse_args()

    out_dir = args.output or Path(r"C:\tmp\today-on-earth-source-frames") / datetime.now().strftime("%Y%m%d-%H%M%S")
    (out_dir / "windows").mkdir(parents=True, exist_ok=True)
    (out_dir / "crops").mkdir(parents=True, exist_ok=True)

    subprocess.Popen([CHROME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    _, window_rect = foreground_chrome()

    sources = extract_sources(args.source_file)
    source_positions = {source["id"]: index for index, source in enumerate(sources, 1)}
    only_ids = [item.strip() for item in args.only_ids.split(",") if item.strip()]
    if only_ids:
        sources = [source for source in sources if source["id"] in only_ids]

    results: list[dict] = []
    for source in sources:
        index = source_positions[source["id"]]
        print(f"[{index}/{len(sources)}] {source['label'] or source['id']} {source['url']}", flush=True)
        try:
            result = capture_source(source, index, window_rect, out_dir, args.wait)
            results.append(result)
            print(f"  ok {result['crop']}", flush=True)
        except Exception as exc:
            results.append({**source, "error": str(exc)})
            print(f"  failed {exc}", flush=True)

    contact = make_contact_sheet(results, out_dir)
    manifest = out_dir / "audit.json"
    manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Audit: {manifest}")
    print(f"Contact sheet: {contact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
