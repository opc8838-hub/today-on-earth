# -*- coding: utf-8 -*-
"""Build a full Today on Earth video with intro and daily source records."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from daily_record import append_run, today_key
from make_sample_video import FFMPEG, run


WORK = Path(__file__).resolve().parent
DEFAULT_INTRO = Path("C:/Users/Administrator/Desktop/微信视频2026-06-06_221529_676.mp4")
OUTPUT_ROOT = Path("C:/tmp/today-on-earth-full")


def print_subprocess_output(text: str) -> None:
    encoding = sys.stdout.encoding or "utf-8"
    safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe_text, end="")


def build_live_body(args: argparse.Namespace) -> tuple[Path, dict]:
    cmd = [
        sys.executable,
        str(WORK / "make_sample_video.py"),
        "--count",
        str(args.count),
        "--duration",
        str(args.duration),
        "--transition",
        str(args.transition),
        "--first-overlay-delay",
        str(args.first_overlay_delay),
        "--sources-file",
        str(args.sources_file),
        "--slot",
        args.slot,
        "--record-date",
        args.record_date,
        "--avoid-daily-record",
    ]
    if args.seed is not None:
        cmd.extend(["--seed", str(args.seed)])

    result = run(cmd, timeout=max(600, round(args.count * args.duration * 40)))
    print_subprocess_output(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-2000:])

    match = re.search(r"Manifest:\s*(.+)", result.stdout)
    if not match:
        raise RuntimeError("Live body render did not print a manifest path.")

    manifest_path = Path(match.group(1).strip())
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return manifest_path, manifest


def combine_intro(intro: Path, live_video: Path, output: Path, silence_seconds: float) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    filter_complex = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1920:1080,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v0];"
        "[1:v]scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v1];"
        "[v0][v1]xfade=transition=fade:duration=0.70:offset=3.33[v];"
        "[0:a]atrim=0:4.034,asetpts=PTS-STARTPTS,afade=t=out:st=3.30:d=0.70[a0];"
        f"anullsrc=channel_layout=stereo:sample_rate=48000,atrim=0:{silence_seconds:.2f}[sil];"
        "[a0][sil]concat=n=2:v=0:a=1[a]"
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
        ],
        timeout=max(240, round(silence_seconds * 12)),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-2000:])
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=7)
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--transition", type=float, default=0.55)
    parser.add_argument("--first-overlay-delay", type=float, default=1.05)
    parser.add_argument("--intro", type=Path, default=DEFAULT_INTRO)
    parser.add_argument("--sources-file", type=Path, default=WORK / "sample_sources.yaml")
    parser.add_argument("--slot", choices=["morning", "afternoon", "manual"], default="manual")
    parser.add_argument("--record-date", default=today_key())
    parser.add_argument("--record-daily-run", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    manifest_path, manifest = build_live_body(args)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = OUTPUT_ROOT / stamp
    output = out_dir / f"today-on-earth-{args.slot}-{args.record_date}-{args.count}-regions.mp4"
    video = combine_intro(args.intro, Path(manifest["horizontal_video"]), output, manifest["duration_seconds"])

    full_manifest = {
        **manifest,
        "render_type": "full_video_with_intro",
        "intro": str(args.intro),
        "live_manifest": str(manifest_path),
        "full_video": str(video),
    }
    full_manifest_path = out_dir / "manifest.full.json"
    full_manifest_path.write_text(json.dumps(full_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.record_daily_run:
        record_file = append_run(
            slot=args.slot,
            source_ids=[source["id"] for source in manifest["sources"]],
            video=str(video),
            cover=manifest["cover"],
            manifest=str(full_manifest_path),
            date_key=args.record_date,
        )
        print(f"Daily record: {record_file}")

    print(f"Full video: {video}")
    print(f"Full manifest: {full_manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
