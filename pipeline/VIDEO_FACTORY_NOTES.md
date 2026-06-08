# Today on Earth Video Factory Notes

Updated: 2026-06-07

## Locked Baseline: Basic Finished Version / 基本成品版

On 2026-06-07 the project reached the "basic finished product" baseline.
Do not lose these decisions when continuing development.

Accepted artifact anchor:

- Accepted video path: `C:\tmp\today-on-earth-full\20260606-224151\today-on-earth-full-7-regions.mp4`
- User playback command: `Invoke-Item "C:\tmp\today-on-earth-full\20260606-224151\today-on-earth-full-7-regions.mp4"`
- File size: 36,890,586 bytes.
- Container duration: 43.015011 seconds.
- Video stream: H.264, 1920x1080, 30 fps, 42.033333 seconds.
- Audio stream: AAC, 43.015011 seconds.
- Check frames in the accepted artifact directory:
  - `C:\tmp\today-on-earth-full\20260606-224151\check_0380.jpg`
  - `C:\tmp\today-on-earth-full\20260606-224151\check_0450.jpg`
  - `C:\tmp\today-on-earth-full\20260606-224151\check_0540.jpg`
- Timeline contact sheet generated from the accepted artifact:
  - `C:\tmp\today-on-earth-full\20260606-224151\accepted_frames\accepted-video-timeline.jpg`

The accepted artifact directory does not contain a manifest. When describing its exact region order, use the actual frame text/timeline, not imagined metadata.

This accepted artifact is the non-regression baseline. When changing locations, preserve the same product feeling:

- Change only live footage, location metadata, weather, and local time.
- Preserve the intro-to-live blend.
- Preserve the top glass information bar geometry.
- Preserve the globe position and edge smoothness.
- Preserve the bilingual city/country layout.
- Preserve the weather row layout.
- Preserve the `Today on Earth` brand spacing.
- Preserve the same calm overlay timing.
- Preserve the premium broadcast mood.

Changing regions must not make the result feel like a raw webcam montage.
If a new render loses the accepted sample's mood, it is a draft failure.

Quality rule:

- Good sources can be normalized to a consistent HD look with 1920x1080 crop, Lanczos scaling, mild contrast/brightness/saturation correction, mild denoise, and mild sharpening.
- Bad sources cannot be forced into the product. If the source is genuinely blurry, low-resolution, heavily compressed, unstable, or dominated by burned-in text, reject or downgrade it instead of over-processing.
- The goal is stable Today on Earth quality, not using every possible camera.

Visible accepted-artifact timeline from extracted frames:

- 0.50s: approved blue/white `Today on Earth` opening visual.
- 2.00s: opening title shows `Today on Earth / 今日地球`.
- 3.80s: intro-to-live blend is visible over Venice footage.
- 4.50s: first live camera visible, information bar not yet fully present.
- 5.40s: first live information bar is fully visible. It shows `Venice 威尼斯, Italy 意大利`.
- 9.80s and 10.60s: second Venice view with the same top-bar style.
- 15.80s and 16.60s: Sydney / 悉尼, Australia / 澳大利亚.
- 21.80s and 22.60s: Shanghai / 上海, China / 中国.
- 27.80s and 28.60s: Rome / 罗马, Italy / 意大利.
- 33.80s and 34.60s: Firostefani / 菲罗斯特法尼, Greece / 希腊.
- 39.80s and 41.80s: Fira / 费拉, Greece / 希腊, final live segment.

Finished video structure:

- Opening: use the approved `Today on Earth / 今日地球` intro clip provided by the user.
- Intro path: `C:\Users\Administrator\Desktop\微信视频2026-06-06_221529_676.mp4`
- Intro duration: about 4 seconds.
- Intro transition: blend the final 0.70 seconds of the intro into the first live camera.
- Live section: 7 regions after the intro.
- Per-region hold: 6 seconds.
- Region transition: natural crossfade, default 0.55 seconds.
- Information bar: first live region appears late, default 1.05 seconds after live starts, so it does not overlap the intro title.
- Information bar: before each region switch, fade out first.
- Information bar disappearance: opacity-only; do not move position while hiding.
- Total duration: about 43 seconds, allowing small encoder/transition rounding differences.
- Music and additional intro treatment are handled by the user separately.

The output must feel like a finished broadcast short, not a technical montage.

## Locked Overlay Direction

The approved information bar direction is the user's reference image:

- `C:\Users\Administrator\Desktop\20260514-002636.jpg`

The overlay must stay close to that visual language:

- Full-screen live footage.
- Top blue-white semi-transparent glass information bar.
- Light-blue globe icon on the left; edges must be smooth.
- City and country shown in English plus Chinese translation.
- Weather row includes temperature, wind speed, humidity, and local time.
- Clean temperature, wind, humidity, and clock icons.
- Right side brand text: `Today on Earth`.
- Brand text must not overlap the decorative arc/icon.
- No text collisions.
- Wind icon must be clean; earlier messy wind mark was rejected.
- The bar appears slowly with a calm broadcast feel.
- It must not pop in, jump, or slide aggressively.
- It must fade out before region changes.

Weather and time are data-driven per source:

- Use source latitude, longitude, and timezone.
- Fetch current weather through the pipeline API when available.
- Render local time per source timezone.
- Fallback weather values are allowed only for internal drafts and must be visible in the manifest.

## Daily Factory Rules

The factory should support daily generation:

- Morning and afternoon runs.
- Do not repeat the same source ID on the same date.
- Daily records live under `pipeline\runs\YYYY-MM-DD.json`.
- When reporting selected regions, always include English and Chinese names.
- Feishu/Lark delivery should include final video path, manifest path, slot/date, duration, and the bilingual source list.

## YouTube Source Audit Baseline

For YouTube sources, do not judge by thumbnails.
Use real Chrome playback frames or actual downloaded clips.

Reusable audit command:

```powershell
python pipeline\audit_youtube_sources.py --source-file "C:\Users\Administrator\Desktop\today-on-earth\镜头源.txt" --wait 45
```

The 2026-06-07 real-frame audit output:

- Full reviewed contact sheet: `C:\tmp\today-on-earth-source-frames\contact-sheet-full-reviewed.png`
- Source review JSON: `C:\tmp\today-on-earth-source-frames\source-review.json`
- Crop frames: `C:\tmp\today-on-earth-source-frames\crops`

Source ratings from the real-frame audit:

- Gold: Seoul Han River / 首尔汉江
- Gold: Seoul Namsan area / 首尔南山视角
- Gold: Sydney skyline / 悉尼天际线
- Gold: Tokyo Live 4K / 东京 4K 城市夜景
- Gold: Chicago Skydeck / 芝加哥观景台
- Gold: Oxford Broad Street / 牛津布罗德街
- Gold: Vancouver / 温哥华
- Gold: Niagara Falls / 尼亚加拉瀑布
- Usable: Tokyo Shinjuku Kabukicho / 东京新宿歌舞伎町
- Usable: Venice Grand Canal / 威尼斯大运河
- Usable: Las Vegas Strip / 拉斯维加斯大道
- Usable: Busan Haeundae / 釜山海云台
- Usable: Tokyo Tower / 东京塔
- Usable: Times Square / 纽约时代广场
- Backup: Sapporo street / 札幌街口
- Backup: New York Upper East Side / 纽约上东区
- Reject: Makkah / 麦加, because burned-in Arabic graphics and crowd density fight the clean broadcast style.
- Reject: Hong Kong / 香港, because large burned-in text and 4K/channel graphics dominate the frame.

Important distinction:

- A real-frame audit proves the source can visually fit the show.
- It does not prove downloader automation is production-stable.
- Before production rendering from YouTube, verify yt-dlp/browser capture separately.

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

## 2026-06-07 Evening Update: Source Pool And YouTube Capture

The user approved a more permissive source policy:

- The whole SkylineWebcams site can be treated as an internal candidate source pool.
- Do not reject Skyline sources only because of fog, low light, backlight, sunset, haze, rain, or ordinary webcam compression.
- Reject only technical failures, page/player/control capture, unreadable footage, giant burned-in graphics, or sources that cannot carry the Today on Earth overlay.
- Keep Skyline legal status as `permission_needed` / `internal_demo` until written authorization or cooperation is secured.

YouTube source test:

- Source document: `C:\Users\Administrator\Desktop\today-on-earth\镜头源.txt`
- Unique YouTube video sources tested: 19
- Clean test artifact: `C:\tmp\today-on-earth-youtube-source-test\20260607-170048-clean18\today-on-earth-youtube-source-test-18-sources-clean.mp4`
- Manifest: `C:\tmp\today-on-earth-youtube-source-test\20260607-170048-clean18\manifest.youtube-source-test.json`
- Timeline: `C:\tmp\today-on-earth-youtube-source-test\20260607-170048-clean18\timeline-4x5.jpg`
- Result: 18 usable sources, 1 unavailable source.
- Excluded source: `VT_5rMtTS3s`, because YouTube displayed an unavailable live-recording message during real playback capture.
- The EarthCam channel page `https://www.youtube.com/@earthcam/streams` was not expanded in this test because it is a channel listing, not a single camera URL.

YouTube quality finding:

- The first all-source browser fallback used a small watch-page player crop of about `1250x704`, then scaled to 1920x1080. This proves source usability but looks only barely HD.
- A higher-quality browser fallback was tested with Oxford:
  - Raw large capture: `C:\tmp\today-on-earth-youtube-hq-test\20260607-oxford-fullscreen\oxford-large-player-crop-1816x1022.mp4`
  - Rendered Today on Earth sample: `C:\tmp\today-on-earth-youtube-hq-test\20260607-oxford-fullscreen\clip_01_h8glPXsnezU.mp4`
- The larger browser capture is visibly better because it records roughly `1816x1022` before normalizing to 1920x1080.
- Browser fallback is still not the target production route. Direct stream capture with a valid logged-in cookie/session path remains preferable when available.

Rules for future YouTube browser fallback:

1. Open the watch page in the user's logged-in Chrome.
2. Verify a precheck screenshot shows real video, not YouTube home, an unavailable page, or a bot/login message.
3. Ensure Feishu/WeChat/desktop windows, Chrome prompts, right chat/sidebar, and YouTube controls are outside the capture region.
4. Prefer large player/fullscreen-style capture around `1816x1022 -> 1920x1080`; avoid `1250x704 -> 1920x1080` for production-looking renders.
5. Apply the same Today on Earth overlay, weather/time data, 6-second timing, overlay fade-out-before-transition rule, and HD normalization.

## 2026-06-07 Late Evening Retry: Low-Overlap Episode

The afternoon/Feishu render repeated too many familiar clusters:

- Shanghai / China
- Venice and Rome / Italy
- Fira and Firostefani / Santorini, Greece
- Kooddoo / Maldives
- Sydney / Australia

The issue was not only repeated `source_id`; it was repeated city clusters and country clusters. Future daily episodes must apply the Source Diversity Contract:

- Avoid same-day `source_id` repeats.
- Avoid repeating city clusters such as Santorini, Venice, Rome, Tokyo, New York, Seoul, or Sydney within the same episode.
- Avoid multiple regions from the same country in a normal 7-region episode when enough alternatives exist.
- Prefer at least 6 countries and at least 4 broad geo-zones for 7 regions.
- Use rolling freshness: avoid the same city cluster for about 72 hours and the same country for about 24 hours when alternatives exist.

Clean low-overlap replacement render:

- Final video: `C:\tmp\today-on-earth-full\20260607-231258-evening-retry\today-on-earth-evening-retry-2026-06-07-7-regions.mp4`
- Manifest: `C:\tmp\today-on-earth-full\20260607-231258-evening-retry\manifest.full.json`
- Timeline: `C:\tmp\today-on-earth-full\20260607-231258-evening-retry\timeline-4x5.jpg`
- Duration: 42.715011 seconds.
- Video: 1920x1080, 30 fps.

Source order:

- Seoul Han River 首尔汉江, South Korea 韩国
- Tokyo Shinjuku 东京新宿, Japan 日本
- Chicago Skydeck 芝加哥观景台, United States 美国
- Makkah 麦加, Saudi Arabia 沙特阿拉伯
- Oxford Broad Street 牛津布罗德街, United Kingdom 英国
- Vancouver 温哥华, Canada 加拿大
- Hong Kong 香港, China 中国

Capture lesson:

- `yt-dlp` direct stream extraction was blocked by YouTube bot checks on this machine, and Chrome cookie extraction failed because the cookie database could not be copied/decrypted.
- YouTube embed/app mode is not reliable because some streams return "Watch on YouTube" / error 153.
- Large/fullscreen browser capture can look sharper, but it can accidentally include YouTube live chat, right sidebars, prompts, or subscription popups.
- The accepted retry used the stable clean player crop because it excluded page UI. It is softer than direct stream or clean fullscreen capture, but it is the correct fallback when the large capture is polluted.
- Never deliver a YouTube browser render until the timeline/contact sheet and several extracted frames confirm there is no page UI in the image.

Feishu/Codex invocation reminder:

```text
使用 today-on-earth-video-factory skill，在 C:\Users\Administrator\codex-projects\today-on-earth 生成今晚的 Today on Earth 视频。
今晚先用 --slot afternoon --record-daily-run；保持 7 个地区、每个 6 秒、片头融合、信息栏 timing，不重复今天早上已经用过的 source_id。完成后把 full video、manifest、地区中英列表发给我。
```
