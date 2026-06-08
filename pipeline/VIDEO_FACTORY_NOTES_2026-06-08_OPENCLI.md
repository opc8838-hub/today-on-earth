# 2026-06-08 OpenCLI Human-Fullscreen Render

Final accepted test render for the 47s YouTube/fullscreen workflow:

- Final video: `C:\tmp\today-on-earth-full\20260608-human-fullscreen-7-final2\today-on-earth-human-fullscreen-2026-06-08-7-regions.mp4`
- Manifest: `C:\tmp\today-on-earth-full\20260608-human-fullscreen-7-final2\manifest.youtube-human-fullscreen.json`
- Timeline: `C:\tmp\today-on-earth-full\20260608-human-fullscreen-7-final2\timeline-4x5.jpg`
- Duration: 47.965011 seconds.
- Video: 1920x1080, 30 fps.
- Timing: 4s intro, 7 regions, `--duration 6.75`, `--transition 0.55`.

Source order:

- Seoul Han River 首尔汉江, South Korea 韩国
- Tokyo Shinjuku 东京新宿, Japan 日本
- Chicago Skydeck 芝加哥观景台, United States 美国
- Makkah 麦加, Saudi Arabia 沙特阿拉伯
- Oxford Broad Street 牛津布罗德街, United Kingdom 英国
- Vancouver 温哥华, Canada 加拿大
- Hong Kong 香港, China 中国

OpenCLI capture lesson:

- Navigate the visible Chrome tab like a human (`Ctrl+L`, paste watch URL, Enter), then bind OpenCLI to that visible tab.
- Do not use address-bar JavaScript injection; it can become a search query.
- Run the video cleanup eval once, press system-level F11 only when `innerHeight < 980`, then run the cleanup eval again.
- Minimize non-Chrome windows before precheck/recording.
- Do not poll logs or inspect screenshots during an active desktop capture; those checks can bring Codex/VSCode/Feishu back into the desktop and contaminate the recording.
- Exit F11 after every recorded source. Without this, later sources may silently record the previous camera even if the labels/weather change.
- Validate the final timeline: it must show seven distinct live views, not only seven different labels.
- Source-burned overlays need source-specific cropping. Tokyo Shinjuku now uses a right/top-biased crop to remove its burned-in weather panel.
