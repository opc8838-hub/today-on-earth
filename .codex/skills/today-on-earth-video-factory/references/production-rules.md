# Production Rules

## Standard Output

Generate complete horizontal videos with:

```powershell
python pipeline\make_full_video.py --slot morning --duration 6.75 --transition 0.55 --record-daily-run
python pipeline\make_full_video.py --slot afternoon --duration 6.75 --transition 0.55 --record-daily-run
```

Use these defaults unless the user overrides them:

- 7 live regions
- 6.75 seconds per region
- 0.55 second live-region crossfade
- 4 second Today on Earth intro
- 0.70 second intro-to-live crossfade
- First live overlay delay: 1.05 seconds
- Expected total duration: about 47.965 seconds

The older 6.00-second / about 43-second timing is a legacy short render. Do not use it for current daily morning/afternoon production unless the user explicitly asks for a short/legacy version.

## Finished Video Contract

The finished product must follow this structure exactly unless the user asks for a different version:

1. Start with the approved `Today on Earth / 今日地球` opening clip.
2. Use the opening clip for about 4 seconds.
3. Blend the final 0.70 seconds of the opening into the first live camera with a natural crossfade.
4. After the opening, show 7 different regions.
5. Each region must hold for 6.75 seconds of live-camera time.
6. Keep natural crossfades between regions, default 0.55 seconds.
7. The information bar must fade out before switching to the next region.
8. The information bar on the first live region must appear late enough to avoid overlapping the intro title, default delay 1.05 seconds.
9. The final video should be about 47.965 seconds long, allowing small encoder/transition rounding differences.
10. Do not add music, voice, or a new title card unless the user explicitly asks; the user handles music and opening assets separately.

If any generated result violates these timing rules, treat it as a draft failure and rerender.

## Accepted Baseline Non-Regression

The most stable accepted sample is the style and motion baseline:

```text
C:\tmp\today-on-earth-full\20260606-224151\today-on-earth-full-7-regions.mp4
```

When changing regions, do not change the show's visual language. Only the live footage, source metadata, weather, and local time should change.

Preserve:

- the approved blue/white opening feel
- the intro-to-live blend
- the top glass information bar geometry
- the globe position and size
- the bilingual city/country layout
- the weather row layout
- the `Today on Earth` brand spacing
- the overlay fade timing
- the calm, premium broadcast mood

Do not accept a render if:

- the information bar jumps, pops, or feels mechanical
- the bar is still visible during a region crossfade
- the bar disappears by moving position instead of fading opacity
- text overlaps or becomes unreadable
- the globe edge becomes rough
- the brand text touches or overlaps the decorative arc/icon
- a new source makes the whole video feel like a raw webcam montage instead of Today on Earth

## Visual Timing

For each live region:

- Start with clean footage.
- Overlay appears slowly with a light upward settle.
- Overlay disappears before the region transitions.
- Overlay disappearance must be opacity-only; do not move it while hiding.
- Never let region crossfade begin while the information bar is still visibly present.
- Never make the overlay pop in abruptly; it should feel like a calm broadcast reveal.

Current accepted overlay timing:

- first live overlay delay: 1.05 seconds
- normal overlay delay: 0.25 seconds
- fade-in duration: about 1.10 seconds
- fade-in motion: very small upward settle only, about -8px to 0px
- fade-out duration: about 0.50 seconds
- fade-out motion: none, opacity only

## Broadcast Overlay Standard

The Today on Earth overlay must match the approved reference style, not a generic lower-third.

Use a top broadcast information bar:

- Canvas: horizontal 1920x1080, 30 fps.
- Video: full-bleed live footage behind the overlay, scaled/cropped to fill 16:9.
- Overlay position: top area, visually centered around y=80-230 on 1920x1080.
- Overlay body: semi-transparent rounded rectangle, blue-white glass style, soft shadow, thin highlight stroke.
- Left element: clean light-blue globe icon partly overlapping the bar; edge must be smooth, no rough outline.
- Main text row: city and country in English plus Chinese, for example `Tokyo 东京` and `Japan 日本`.
- Weather row: temperature, wind speed, humidity, local time.
- Icons: simple white/blue line icons; wind icon must be clean and readable.
- Brand area: right side text `Today on Earth`, with enough spacing so it never overlaps the decorative arc/icon.
- Typography: clean sans-serif, readable, no negative letter spacing, no text collision.
- Source/watermark: do not remove platform branding in public/commercial renders. For internal demos, avoid sources with large burned-in marks when cleaner alternatives exist.

Information bar content must be data-driven per source:

- City: English + Chinese translation.
- Country/region: English + Chinese translation.
- Weather: current temperature in Celsius, wind speed in km/h, humidity percentage.
- Time: current local time for that source timezone.
- Weather/time data should come from the pipeline API when latitude, longitude and timezone are available; fallback values are allowed only for internal drafts and must be visible in the manifest.

Do not use:

- bottom information bars for the main location/weather identity
- large opaque boxes
- text-only overlays without icons
- rough globe edges
- fast pop-in animation
- moving overlay while it disappears

## Quality Checks

After generation:

- Run `ffprobe` or inspect printed duration.
- Open the final MP4 with `Invoke-Item`.
- Confirm the intro is the approved `Today on Earth / 今日地球` opening.
- Confirm the intro blends into live footage during the last 0.70 seconds, not by a hard cut.
- Check the first transition from intro to live.
- Check at least one mid-video region transition.
- Check that each live region stays on screen for 6.75 seconds.
- Check that the information bar fades out before each region switch.
- Check that the first live information bar appears after the intro title clears.
- Check that the final duration is about 47.965 seconds.
- Check the final manifest for source IDs, local time, and weather.
- Check the final source list against `references/source-selection.md`: no repeated city cluster or avoidable country cluster in a normal 7-region episode.
- When reporting sources to the user or Feishu, include city/country in both English and Chinese.

## Source Frame Acceptance

Before adding a new live source to production, inspect a real playback frame or captured clip, not a thumbnail.

Accept a source only when:

- actual playback loads in the browser or downloader
- visible frame is at least HD-looking after crop to 1920x1080
- scene can carry the Today on Earth overlay without fighting it
- camera has stable framing and no giant burned-in captions
- page/player controls are not part of the captured video material

Rate each source:

- `gold`: clean, high-definition, broad scenic or city view
- `usable`: good enough with crop/color/sharpening
- `backup`: usable only for variety or special scenes
- `reject`: blank, unavailable, too low quality, or dominated by baked-in text/graphics

For YouTube sources, if yt-dlp is blocked, use the user's real Chrome session to capture frames for review, but do not mark it production-stable until clip download is verified.

## 2026-06-07 Source Policy Update

SkylineWebcams:

- Treat the entire SkylineWebcams site as an approved internal candidate source pool.
- Natural quality variation is acceptable: fog, low light, backlight, sunset, haze, rain, and imperfect webcam color are not rejection reasons by themselves.
- Reject only technical failures, player/page/control capture, unreadable footage, giant burned-in overlays, or sources that cannot carry the Today on Earth overlay.
- Continue to mark rights as `permission_needed` and usage as `internal_demo` until there is written permission or partnership clearance.

YouTube:

- The source list at `C:\Users\Administrator\Desktop\today-on-earth\镜头源.txt` was tested on 2026-06-07.
- Clean test artifact: `C:\tmp\today-on-earth-youtube-source-test\20260607-170048-clean18\today-on-earth-youtube-source-test-18-sources-clean.mp4`.
- Manifest: `C:\tmp\today-on-earth-youtube-source-test\20260607-170048-clean18\manifest.youtube-source-test.json`.
- Result: 18 usable YouTube sources, 1 unavailable source (`VT_5rMtTS3s`, YouTube displayed an unavailable live-recording message).
- YouTube sources are usable as supplements, but browser recording is still a fallback. Direct stream capture with a valid login/cookie path is the desired production route when available.

YouTube browser fallback:

- Do not rely on a small watch-page player crop for finished production if a larger capture is possible.
- The small fallback used in the all-source test was about `1250x704 -> 1920x1080`; this is only barely HD and can look soft.
- The improved fallback tested on Oxford used a larger player/fullscreen-style crop around `1816x1022 -> 1920x1080`, producing a sharper internal sample:
  `C:\tmp\today-on-earth-youtube-hq-test\20260607-oxford-fullscreen\clip_01_h8glPXsnezU.mp4`.
- Always make a precheck screenshot before recording. The browser must show real video, not YouTube home, an error page, live chat, Chrome UI, Feishu/WeChat overlays, or desktop windows.
- Large/fullscreen browser capture must be verified per source. If the final timeline shows YouTube sidebars, live chat, prompts, subscription popups, or browser/page UI, the render is a draft failure.
- If direct stream capture is blocked and large browser capture is polluted, use the stable clean player crop rather than delivering a visibly contaminated video. Report that this is a clean fallback with softer source quality.

## Footage Quality Normalization

Normalize accepted footage to a consistent HD look, but do not pretend bad sources are good.

Use conservative enhancement:

- scale/crop to 1920x1080
- prefer Lanczos scaling
- normalize to 30 fps
- mild contrast/brightness/saturation correction
- mild denoise
- mild sharpening

Reject or downgrade a source instead of forcing it when:

- the original stream is genuinely low-resolution
- compression artifacts dominate
- motion blur is severe
- burned-in text/graphics dominate
- the camera is unstable or poorly framed
- the scene cannot carry the top information bar cleanly

The factory can polish good footage. It cannot make a poor stream truly high-definition without changing the product quality standard.

## Timing Contract

For a standard complete video:

- intro duration: 4 seconds
- intro-to-live crossfade: 0.70 seconds
- live regions: 7
- each live region: 6.75 seconds
- live-region crossfade: 0.55 seconds
- first live overlay delay: 1.05 seconds
- normal overlay delay: 0.25 seconds
- overlay fade-in: about 1.10 seconds, slow and breathable
- overlay fade-out: starts before the live-region transition and uses opacity only

## Current Intro

Use:

```text
C:\Users\Administrator\Desktop\微信视频2026-06-06_221529_676.mp4
```

If the file is missing, ask the user for the intro path before generating a full video.
