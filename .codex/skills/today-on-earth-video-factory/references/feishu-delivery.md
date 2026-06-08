# Feishu / Lark Delivery

Use this when the user says things like:

- 发我
- 发到飞书
- 调用飞书桥接
- 把成品发给我

## What To Send

Send a concise production summary:

- Final video path
- Full manifest path
- Slot/date
- Duration
- Source list with English and Chinese names, e.g. `Sydney 悉尼, Australia 澳大利亚`
- Any failed or skipped source

Attach or upload the final MP4 when the available Feishu/Lark bridge supports file upload.

## Message Template

```text
今日地球 {slot} 已生成

视频：{final_video}
Manifest：{manifest}
时长：{duration}
地区：{source_titles}
地区列表必须带中文翻译。
备注：内部测试源，公开发布前需确认授权。
```

## Tooling

Prefer the user's existing Codex-to-Feishu bridge. If a Lark/Feishu MCP skill or CLI is available in the current session, use that bridge. If no bridge tool is available, report the final paths and tell the user the file is ready locally.
