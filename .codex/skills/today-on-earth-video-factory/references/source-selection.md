# Source Selection

## Daily Record

Daily run records live in:

```text
pipeline\runs\YYYY-MM-DD.json
```

Each record stores:

- slot: `morning`, `afternoon`, or `manual`
- created time
- source IDs
- final video path
- cover path
- manifest path

## No Repeat Rule

For the same date:

- Do not repeat the same `source_id`.
- Prefer not to repeat the same city.
- Prefer not to cluster the same country unless the source library is too small.

If there are not enough unused sources:

1. Report how many unused sources remain.
2. Ask whether to render fewer regions or allow repeats.
3. If repeats are allowed, note the reason in the response.

## Source Diversity Contract

For a normal 7-region Today on Earth episode, source selection must avoid the "same places again" feeling, not only literal `source_id` repeats.

Hard rules unless the user explicitly requests a themed episode:

- Use 7 different `source_id` values.
- Use 7 different city clusters when enough playable sources exist.
- Do not use two cameras from the same city cluster in one episode.
- Do not use two regions from the same country in one episode when at least 7 playable countries are available.
- Prefer at least 6 countries and at least 4 broad geo-zones in a 7-region episode.
- Morning sources block evening/afternoon reuse by `source_id`, city cluster, and obvious country/scene cluster when alternatives exist.

Rolling freshness rules:

- Avoid repeating the same `source_id` for the same date.
- Avoid repeating the same city cluster for 72 hours when enough playable alternatives exist.
- Avoid repeating the same country within 24 hours when enough playable alternatives exist.
- If a rerender replaces a bad episode, record the replacement run and treat its sources as used too.

City cluster examples:

- `santorini`: Fira, Firostefani, Oia, Santorini caldera cameras.
- `venice`: San Marco, Rialto, Grand Canal, lagoon cameras.
- `rome`: Trevi, Colosseum, Spanish Steps, central Rome cameras.
- `tokyo`: Tokyo, Shinjuku, Tokyo Tower, Kabukicho.
- `new_york`: Times Square, Upper East Side, Brooklyn/Manhattan skyline.
- `seoul`: Seoul Han River, Namsan, central Seoul views.
- `sydney`: Sydney Harbour, Opera House, skyline cameras.

When a source list is small, choose variety in this order:

1. Different city cluster.
2. Different country.
3. Different broad geo-zone.
4. Different scene type.
5. Better technical quality.

If these rules cannot be satisfied, say exactly what is repeated and why before rendering or in the final delivery note.

## Preferred Mix

For a 7-region video, prefer:

- 2 city/skyline scenes
- 2 landmark/public square scenes
- 1 island/beach scene
- 1 harbor/water scene
- 1 visually distinct wild-card scene

Use source metadata and current availability rather than forcing this mix when streams are down.

## Day / Night Mix

Night footage is not a failure state. A complete Today on Earth episode should show real time-zone differences across Earth, so night scenes should remain in the rotation.

Use these lightweight classes during source review:

- `night_city_good`: city lights, harbors, roads, public squares, or other night views with readable visual content. Usable.
- `night_nature_weak`: beaches, mountains, lakes, coasts, islands, or rural scenes with faint moonlight, skyline glow, or a few lights. Usable.
- `too_dark`: nearly pure black, no readable place/skyline/scene information, or technically unreadable footage. Skip for the current render only; do not permanently blacklist.

For a normal 7-region episode:

- 2-3 `night_city_good` or `night_nature_weak` clips are acceptable.
- Avoid 4-5 mostly dark clips in one episode unless the user explicitly asks for a night-themed render.
- Do not use local time or darkness as a hard exclusion. Use the episode-level ratio to keep coverage broad while still rotating through the full Skyline source pool over time.

## Skyline Candidate Rule

As of 2026-06-07, the user approved the whole SkylineWebcams site as an internal candidate source pool.

Selection should be permissive:

- Accept normal live-webcam imperfections such as fog, low light, sunrise/sunset glare, haze, rain, and ordinary webcam compression.
- Do not remove a Skyline candidate just because the weather or time of day is not ideal.
- Reject only technical failures, page/player capture, unreadable footage, giant burned-in graphics, or sources that cannot carry the Today on Earth overlay.
- For public/commercial release, keep `rights_status: permission_needed` until authorization is handled.

## YouTube Source Audit

When the user provides YouTube live sources, do not judge them from thumbnails.

Use the project audit tool with the user's visible Chrome session:

```powershell
python pipeline\audit_youtube_sources.py --source-file "C:\Users\Administrator\Desktop\today-on-earth\闀滃ご婧?txt" --wait 45
```

The tool outputs:

- `audit.json`
- `contact-sheet.png`
- full Chrome screenshots
- player-area crops

If a source is blank on the first pass, retry it with a longer wait and `--only-ids`:

```powershell
python pipeline\audit_youtube_sources.py --source-file "C:\Users\Administrator\Desktop\today-on-earth\闀滃ご婧?txt" --wait 45 --only-ids "VIDEO_ID"
```

Only promote a YouTube source after a real playback frame is inspected. A good frame does not mean download automation is stable; verify yt-dlp or browser capture separately before production rendering.

## YouTube Browser Fallback

If `yt-dlp` or direct stream extraction is blocked:

1. Reuse the user's logged-in Chrome session.
2. Open the YouTube watch page and verify real playback with a screenshot.
3. For finished-looking internal tests, prefer a large player/fullscreen-style crop around `1816x1022` instead of the old `1250x704` player crop.
4. Make sure no Feishu/WeChat window, Chrome prompt, live chat, or YouTube controls are in the capture region.
5. Normalize to 1920x1080, apply the normal Today on Earth overlay, and note in the manifest that browser capture was used.

Known 2026-06-07 YouTube test result:

- Clean test video: `C:\tmp\today-on-earth-youtube-source-test\20260607-170048-clean18\today-on-earth-youtube-source-test-18-sources-clean.mp4`
- 18 usable sources.
- `VT_5rMtTS3s` is currently unavailable and should be skipped unless it later plays normally.
