# -*- coding: utf-8 -*-
"""Today on Earth — Source Health Checker

Checks all sources in sources.yaml for live status.
Run: python health_check.py [--update-yaml]

Output:
  - Console report: active/degraded/inactive counts by continent
  - If --update-yaml: writes updated status back to sources.yaml
"""

import subprocess, sys, os, yaml
from datetime import datetime, timezone

# Force UTF-8 on Windows to avoid GBK encoding errors
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WORK = os.path.dirname(os.path.abspath(__file__))
SOURCES_FILE = os.path.join(WORK, "sources.yaml")

def load_sources():
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["sources"]

def save_sources(sources):
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    # Simple approach: overwrite
    with open(SOURCES_FILE, "w", encoding="utf-8") as f:
        f.write("# Today on Earth — Video Source Database\n")
        f.write("# Auto-updated: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC") + "\n")
        f.write("# =========================================\n\n")
        yaml.dump({"sources": sources}, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def check_source(src):
    """Check if a YouTube live stream is currently live and reachable."""
    url = src["url"]
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--dump-json", "--playlist-end", "1", url],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=15
        )
        if result.returncode != 0:
            return False, f"yt-dlp error: {result.stderr[:100]}"

        import json
        data = json.loads(result.stdout.strip())
        live_status = data.get("live_status", "unknown")
        title = data.get("title", "?")

        if live_status == "is_live":
            return True, f"LIVE: {title[:60]}"
        else:
            return False, f"NOT live ({live_status}): {title[:60]}"
    except subprocess.TimeoutExpired:
        return False, "timeout (15s)"
    except Exception as e:
        return False, f"exception: {str(e)[:80]}"

def auto_search(query, n=5):
    """Search YouTube for potential new sources."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--dump-json", f"ytsearch{n}:{query}"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=20
        )
        if result.returncode != 0:
            return []

        import json
        candidates = []
        for line in result.stdout.strip().split("\n"):
            d = json.loads(line)
            if d.get("live_status") == "is_live":
                candidates.append({
                    "id": d.get("id"),
                    "title": d.get("title", "?"),
                    "url": f"https://www.youtube.com/watch?v={d.get('id')}",
                })
        return candidates
    except:
        return []

def main():
    update = "--update-yaml" in sys.argv

    print("=" * 60)
    print("Today on Earth — Health Check")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    sources = load_sources()
    results = {"active": 0, "degraded": 0, "inactive": 0, "newly_broken": [], "newly_recovered": []}
    by_continent = {}

    for src in sources:
        print(f"\n  [{src['id']}] {src['city_cn']}, {src['country_cn']} ...", end=" ", flush=True)
        ok, msg = check_source(src)
        print(msg)

        # Group by continent
        continent = src.get("timezone", "UTC").split("/")[0]
        if continent not in by_continent:
            by_continent[continent] = {"total": 0, "active": 0}
        by_continent[continent]["total"] += 1

        prev_status = src.get("status", "active")

        if ok:
            src["failures"] = 0
            src["last_ok"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if prev_status == "inactive":
                src["status"] = "degraded"
                results["newly_recovered"].append(src["id"])
            elif prev_status == "degraded":
                src["status"] = "active"
                results["newly_recovered"].append(src["id"])
            else:
                src["status"] = "active"
            results["active"] += 1
            by_continent[continent]["active"] += 1
        else:
            src["failures"] += 1
            if src["failures"] >= 3:
                if prev_status != "inactive":
                    results["newly_broken"].append(src["id"])
                src["status"] = "inactive"
                results["inactive"] += 1
            elif src["failures"] > 0:
                src["status"] = "degraded"
                results["degraded"] += 1

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = len(sources)
    print(f"  Total sources: {total}")
    print(f"  Active:   {results['active']} ({100*results['active']//total}%)")
    print(f"  Degraded: {results['degraded']}")
    print(f"  Inactive: {results['inactive']}")

    print("\n  By continent:")
    for cont in sorted(by_continent.keys()):
        d = by_continent[cont]
        print(f"    {cont}: {d['active']}/{d['total']} active")

    if results["newly_broken"]:
        print(f"\n  ⚠ Newly broken: {', '.join(results['newly_broken'])}")
    if results["newly_recovered"]:
        print(f"\n  ✅ Newly recovered: {', '.join(results['newly_recovered'])}")

    # Auto-search for replacements if gaps
    if results["inactive"] > 3:
        print("\n  🔍 Auto-searching for replacements...")
        for src in sources:
            if src["status"] == "inactive":
                candidates = auto_search(f"live webcam {src['city_en']}")
                if candidates:
                    print(f"    For {src['city_cn']}:")
                    for c in candidates[:3]:
                        print(f"      - {c['title'][:60]}")

    if update:
        save_sources(sources)
        print("\n✅ sources.yaml updated.")

    print("\nDone.")

if __name__ == "__main__":
    main()
