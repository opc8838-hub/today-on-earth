# -*- coding: utf-8 -*-
"""SkylineWebcams scraper — pulls ALL live webcams from skylinewebcams.com
Outputs YAML entries ready for sources.yaml
"""
import urllib.request, re, json, time, sys, yaml
from urllib.parse import urljoin

BASE = "https://www.skylinewebcams.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8")

def get_country_pages():
    """Get all country listing page URLs"""
    html = fetch(f"{BASE}/en/webcam/")
    links = re.findall(r'href="(/en/webcam/[a-z-]+\.html)"', html)
    return sorted(set(links))

def get_webcam_pages(country_url):
    """Get all webcam page URLs from a country listing"""
    html = fetch(f"{BASE}{country_url}")
    links = re.findall(r'href="(/en/webcam/[^"]+\.html)"', html)
    return sorted(set(links))

def extract_stream_info(webcam_url):
    """Extract m3u8 stream URL and metadata from a webcam page"""
    try:
        html = fetch(f"{BASE}{webcam_url}")
    except:
        return None

    # Extract m3u8 source from Clappr player config
    m3u8_match = re.search(r"source:\s*'([^']+\.m3u8[^']*)'", html)
    if not m3u8_match:
        m3u8_match = re.search(r'source:\s*"([^"]+\.m3u8[^"]*)"', html)

    # Extract title
    title_match = re.search(r"<title>([^<]+)</title>", html)
    title = title_match.group(1) if title_match else webcam_url

    # Extract CDN image/ID
    cdn_match = re.search(r"//cdn\.skylinewebcams\.com/(\d+)\.json", html)
    webcam_id = cdn_match.group(1) if cdn_match else "unknown"

    # Try to find if it's a YouTube embed
    yt_match = re.search(r'youtube\.com/(?:embed|watch\?v=)/([a-zA-Z0-9_-]+)', html)

    result = {
        "page_url": f"{BASE}{webcam_url}",
        "title": title.strip(),
        "webcam_id": webcam_id,
    }

    if m3u8_match:
        m3u8 = m3u8_match.group(1)
        if m3u8.startswith("//"):
            m3u8 = "https:" + m3u8
        elif not m3u8.startswith("http"):
            m3u8 = f"https://cdn.skylinewebcams.com/{m3u8}"
        result["stream_url"] = m3u8
        result["platform"] = "skylinewebcams_hls"
    elif yt_match:
        result["platform"] = "youtube_live"
        result["stream_url"] = f"https://www.youtube.com/watch?v={yt_match.group(1)}"
    else:
        result["platform"] = "unknown"
        result["stream_url"] = None

    return result

def main():
    print("Fetching country list...")
    countries = get_country_pages()
    print(f"Found {len(countries)} countries")

    all_webcams = []
    for i, country in enumerate(countries):
        try:
            pages = get_webcam_pages(country)
            print(f"  [{i+1}/{len(countries)}] {country}: {len(pages)} webcams")
            for page in pages:
                info = extract_stream_info(page)
                if info:
                    all_webcams.append(info)
            time.sleep(1)  # Be polite
        except Exception as e:
            print(f"  [{i+1}/{len(countries)}] {country}: ERROR - {e}")

    print(f"\nTotal webcams found: {len(all_webcams)}")
    print(f"  HLS streams: {sum(1 for w in all_webcams if w['platform'] == 'skylinewebcams_hls')}")
    print(f"  YouTube:     {sum(1 for w in all_webcams if w['platform'] == 'youtube_live')}")
    print(f"  Unknown:     {sum(1 for w in all_webcams if w['platform'] == 'unknown')}")

    # Save to JSON for review
    output_path = r"C:\Users\Administrator\earth-sources\skylinewebcams_all.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_webcams, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    main()
