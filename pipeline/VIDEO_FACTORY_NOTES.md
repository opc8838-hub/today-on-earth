# Today on Earth Video Factory Notes

Updated: 2026-05-19

## Current Direction

The first video factory prototype should focus on:

- Fetching clean real-time webcam clips.
- Compositing multiple places into one short video.
- Normalizing footage to a consistent HD look.
- Rendering a fixed top information bar.
- Syncing each location with its own local time and weather data.

Intro animation and music will be handled separately.

## SkylineWebcams Source Decision

SkylineWebcams is currently one of the most useful source pools because it has many global real-time public cameras.

Important distinction:

- Use Skyline single webcam pages, for example `skyline_venice_san_marco`.
- Do not use Skyline YouTube aggregation streams such as "1200 TOP LIVE WEBCAMS".

Reason:

- Direct Skyline single-page HLS streams are generally clean.
- The Skyline page player watermark is an HTML/SVG overlay, not burned into the HLS stream.
- YouTube aggregation streams may already contain burned-in Skyline logo, map, QR code, lower thirds, and other program packaging.

Tested direct HLS extraction:

- Page: `https://www.skylinewebcams.com/en/webcam/italia/veneto/venezia/piazza-san-marco.html`
- HLS pattern: `https://hd-auth.skylinewebcams.com/live.m3u8?a=<token>`
- Raw test output: `C:\tmp\skyline-raw-watermark-test\20260519-230029\skyline_raw_venice_san_marco.mp4`
- Frame: `C:\tmp\skyline-raw-watermark-test\20260519-230029\frame_02s.jpg`

Conclusion:

Direct Skyline single webcam HLS is clean enough for internal sample rendering. Some individual cameras may still have hardware-burned marks; those should be reviewed per source and handled by crop/delogo only when needed.

## Rights Status

All Skyline usage is currently marked as:

- `rights_status: permission_needed`
- `usage_mode: internal_demo`

This is intentional. The current work is for private testing and visual tuning. Before public or commercial release, request written permission or negotiate cooperation.

## Implemented Prototype

Files:

- `pipeline/sample_sources.yaml`
- `pipeline/make_sample_video.py`
- `pipeline/scrape_skyline.py`

What works:

- Extracts direct Skyline single-page HLS from `livee.m3u8?a=<token>`.
- Converts it to `https://hd-auth.skylinewebcams.com/live.m3u8?a=<token>`.
- Captures short clips.
- Normalizes to 1920x1080.
- Adds a top information bar inspired by the provided mockup/reference.
- Calls Open-Meteo per source using latitude/longitude/timezone.
- Renders temperature, wind speed, humidity, and local time per clip.
- Writes weather/local-time data into `manifest.json`.

Run:

```powershell
python pipeline\make_sample_video.py --count 2 --duration 5
```

Latest usable sample:

- `C:\tmp\today-on-earth-samples\20260519-232253\today-on-earth-sample-horizontal.mp4`

## Visual Reference

Target visual style:

- Full-screen real webcam footage.
- Top floating glass information bar.
- Blue/white earth and weather feeling.
- City and country in English + Chinese.
- Weather row: temperature, wind, humidity, local time.
- Right side: `Today on Earth`.
- Calm global TV-column feeling.

The supplied mockup image is the main target:

- `C:\Users\Administrator\Desktop\20260514-002636.jpg`

Additional motion reference:

- `C:\Users\Administrator\Desktop\飞书20260519-231645.qt`

Observed from the motion reference:

- The information bar appears per location segment.
- It is not simply fixed for the entire video.
- It fades or disappears before/around location changes.
- The old reference uses green/white; Today on Earth should use the newer blue/white glass style.

## Current Problem

The current top-bar entrance animation is not elegant enough.

It technically works, but the feel is too mechanical:

- The slide-in is too literal.
- The glass panel lacks polished rounded shape and true softness.
- The earth icon is a temporary text/vector placeholder.
- Weather icons are text placeholders.

Do not continue building more video features until the top-bar motion and visual template are refined.

## Recommended Next Step

Replace the FFmpeg-only drawn top bar with a reusable overlay asset/template:

1. Create a transparent PNG or short MOV/WebM alpha overlay for the glass bar.
2. Use real icon assets for:
   - Earth/globe
   - Temperature
   - Wind
   - Humidity
   - Time
3. Keep dynamic text rendered by FFmpeg or generate per-clip transparent overlays.
4. Rework animation to feel like a soft TV broadcast reveal:
   - Short fade-in.
   - Slight horizontal drift or mask reveal.
   - No aggressive sliding.
   - Fade down before clip transition.

The video factory should pause at this checkpoint until the visual language feels right.
