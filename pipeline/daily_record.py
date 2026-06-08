# -*- coding: utf-8 -*-
"""Daily source-usage records for Today on Earth renders."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


WORK = Path(__file__).resolve().parent
RUNS_DIR = WORK / "runs"
LOCAL_TZ = ZoneInfo("Asia/Shanghai")


def today_key() -> str:
    return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")


def record_path(date_key: str | None = None) -> Path:
    return RUNS_DIR / f"{date_key or today_key()}.json"


def load_record(date_key: str | None = None) -> dict:
    path = record_path(date_key)
    if not path.exists():
        return {"date": date_key or today_key(), "runs": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_record(record: dict) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = record_path(record["date"])
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def used_source_ids(record: dict) -> set[str]:
    used: set[str] = set()
    for run in record.get("runs", []):
        used.update(run.get("source_ids", []))
    return used


def append_run(
    *,
    slot: str,
    source_ids: list[str],
    video: str,
    cover: str,
    manifest: str,
    date_key: str | None = None,
) -> Path:
    record = load_record(date_key)
    record.setdefault("runs", []).append(
        {
            "slot": slot,
            "created_at": datetime.now(LOCAL_TZ).isoformat(timespec="seconds"),
            "source_ids": source_ids,
            "video": video,
            "cover": cover,
            "manifest": manifest,
        }
    )
    return save_record(record)
