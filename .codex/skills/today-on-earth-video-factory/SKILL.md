---
name: today-on-earth-video-factory
description: Generate, review, and deliver Today on Earth / 今日地球 finished videos from the local today-on-earth repo. Use when the user asks to make morning/afternoon daily videos, combine the Today on Earth intro with live SkylineWebcams footage, select non-repeating daily sources, render weather/location overlays, produce final video files, or send completed videos via the user's Feishu/Lark bridge.
---

# Today on Earth Video Factory

## Default Workflow

Work in:

```powershell
cd C:\Users\Administrator\codex-projects\today-on-earth
```

Use the full-video script for normal production:

```powershell
python pipeline\make_full_video.py --slot morning --duration 6.75 --transition 0.55 --record-daily-run
python pipeline\make_full_video.py --slot afternoon --duration 6.75 --transition 0.55 --record-daily-run
```

Current timing default, effective 2026-06-08 onward:

- Use 7 regions x 6.75 seconds, not the older 6.00-second hold.
- Keep the 0.55 second live-region crossfade and 0.70 second intro-to-live crossfade.
- Expected finished duration is about 47.965 seconds.
- Treat older 6.00-second / about 43-second renders as legacy/short versions. Only use them when the user explicitly asks for a short/legacy 43-second render.
- If this skill conflicts with a dated project note, the newest dated note wins. Read `pipeline\VIDEO_FACTORY_NOTES_2026-06-08_OPENCLI.md` before rendering any current daily video.

Feishu/Codex invocation example:

```text
Use today-on-earth-video-factory skill in C:\Users\Administrator\codex-projects\today-on-earth to generate today's morning/afternoon Today on Earth video. Use --slot morning or --slot afternoon with --duration 6.75 --transition 0.55 --record-daily-run; keep 7 regions, intro blend, information-bar timing, and do not repeat today's already-used source_id values. Send the full video, manifest, and bilingual region list.
```

Defaults:

- Intro: `C:\Users\Administrator\Desktop\微信视频2026-06-06_221529_676.mp4`
- Opening: approved `Today on Earth / 今日地球` intro clip
- Intro-to-live blend: final 0.70 seconds of intro crossfade into first live camera
- Live sources: 7 regions
- Per-region duration: 6.75 seconds
- Region transition: 0.55 second crossfade
- First live overlay delay: 1.05 seconds, to avoid overlapping the intro title
- Information bar: fade out before each region switch; do not move while hiding
- Expected total duration: about 47.965 seconds
- Output root: `C:\tmp\today-on-earth-full`
- Daily source records: `pipeline\runs\YYYY-MM-DD.json`

## Operating Rules

- Current daily morning/afternoon productions MUST pass `--duration 6.75 --transition 0.55` unless the user explicitly asks for a shorter legacy render.
- If the user mentions updated rules, overnight/last-night Codex changes, at-least-47-seconds timing, OpenCLI, YouTube fullscreen, or human fullscreen, read `pipeline\VIDEO_FACTORY_NOTES_2026-06-08_OPENCLI.md` before choosing commands.
- Before rendering or judging source quality, read `references/production-rules.md` and follow the Broadcast Overlay Standard, Source Frame Acceptance, and Timing Contract.
- If the user refers to the "basic finished product", "基本成品", previous visual decisions, or asks to remember the current style, read `pipeline\VIDEO_FACTORY_NOTES.md` in the repo and preserve the locked 2026-06-07 baseline.
- Always inspect the final `Full video:` and `Full manifest:` paths printed by the script.
- When reporting the region list, include English and Chinese names, e.g. `Sydney 悉尼, Australia 澳大利亚`.
- Do not repeat source IDs within the same date. Morning sources block afternoon reuse.
- Enforce the Source Diversity Contract in `references/source-selection.md`: do not make a normal 7-region episode from repeated city clusters or repeated countries when alternatives exist.
- Prefer global variety over convenient source availability.
- Daily source selection should be random and flexible across the large SkylineWebcams pool and the user's curated YouTube list at `C:\Users\Administrator\Desktop\today-on-earth\镜头源.txt`. Do not use fixed provider quotas. YouTube sources in that file are manually selected by the user and may be used whenever they pass the normal non-repeat, geography, and final timeline checks.
- Keep the legal status as internal/demo unless the user explicitly says the source is cleared.
- If source/weather fetching fails transiently, retry once before changing sources.
- If there are not enough unused sources for the afternoon, report the shortage before allowing repeats.

## Current Source Policy

- SkylineWebcams: the whole Skyline site can be used as an internal candidate source pool. Do not reject a Skyline source only because of fog, low light, backlight, sunset, ordinary haze, or imperfect weather. Reject only technical failures, page/control capture, unreadable footage, giant burned-in overlays, or a source that cannot survive the Today on Earth render.
- YouTube: usable as a supplemental source pool. Direct stream capture is preferred when cookies/login automation works. Browser capture is a fallback, not the quality target.
- YouTube browser fallback quality rule: avoid the old small player crop (`1250x704 -> 1920x1080`) for finished production when possible. Prefer a larger Chrome/YouTube player capture after real playback precheck, around `1816x1022 -> 1920x1080`, then apply the normal HD normalization and overlay.
- Large/fullscreen YouTube browser capture is not automatically safe: it can accidentally include live chat, right sidebars, prompts, or subscription popups. Validate every rendered source with timeline frames. If any page UI appears, rerender with direct stream capture or the stable clean player crop and report the quality tradeoff.
- Before browser fallback recording, verify the desktop is clean: no Feishu/WeChat windows over the browser, no YouTube error page, no right chat/sidebar in the capture, no browser controls in the crop.
- 2026-06-07 all-source YouTube test: clean result path is `C:\tmp\today-on-earth-youtube-source-test\20260607-170048-clean18\today-on-earth-youtube-source-test-18-sources-clean.mp4`; 18 usable sources, 1 unavailable source (`VT_5rMtTS3s`).
- 2026-06-07 low-overlap evening retry: final clean fallback render is `C:\tmp\today-on-earth-full\20260607-231258-evening-retry\today-on-earth-evening-retry-2026-06-07-7-regions.mp4`.
- 2026-06-08 OpenCLI human-fullscreen render: final path is `C:\tmp\today-on-earth-full\20260608-human-fullscreen-7-final2\today-on-earth-human-fullscreen-2026-06-08-7-regions.mp4`; duration is 47.965s; 7 sources x 6.75s with 0.55s transitions.

## YouTube Human-Fullscreen Capture Rules

- Use OpenCLI only after the visible Chrome tab is navigated like a human: foreground Chrome, `Ctrl+L`, paste the watch URL, press Enter, wait for real playback, then `opencli browser <session> bind`.
- Do not use address-bar `javascript:` injection. It can turn into a search query and wastes the browser state.
- After binding, evaluate the video-cleanup script that removes chat/sidebar/page chrome, moves the real `<video>` into a fixed full-viewport host, requests `hd1080`, mutes, and plays.
- If `window.innerHeight < 980` on a 1080p screen, press system-level F11, wait, then evaluate the cleanup script a second time. If `innerHeight` is around 1024, treat it as the OpenCLI/debug-bar fullscreen state and do not toggle again.
- Before `gdigrab`, minimize non-Chrome visible windows and close the Chrome/OpenCLI debug infobar. Do not poll logs, inspect images, or interact with the desktop while recording is in progress; that can bring Codex/VSCode/Feishu back into the capture.
- After each human-fullscreen segment is recorded, press system-level F11 to exit fullscreen before navigating to the next source. This prevents the next segment from silently re-recording the previous camera.
- Always inspect the final timeline/contact sheet after the render. Passing `hd1080` logs is not enough; confirm each region actually changes and no browser UI appears.
- For the user's "at least 47 seconds" version, use `--duration 6.75 --transition 0.55` for 7 regions plus the 4s intro. This gives about 47.965 seconds after intro crossfade.
- Source-burned overlays are handled with source-specific crops, not fake blur/paint, unless the user explicitly asks for a repair pass. Example: Tokyo Shinjuku uses a right/top-biased crop to remove its burned-in weather panel.

## References

Read only the relevant file:

- `references/production-rules.md` for render timings and output checks.
- `references/source-selection.md` for daily source rotation rules.
- `references/feishu-delivery.md` when the user asks to send or bridge the finished video to Feishu/Lark.
- `pipeline/VIDEO_FACTORY_NOTES_2026-06-08_OPENCLI.md` for the OpenCLI human-fullscreen YouTube capture workflow and its failure modes.
