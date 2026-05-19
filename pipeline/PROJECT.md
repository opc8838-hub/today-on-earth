# Today on Earth｜今日地球

> 每天两次，随机看看此刻的地球。  
> 一个每日更新的全球影像栏目——用 AI 重新打开看世界的窗口。

---

## 项目状态

**阶段：源池完成 + 管线验证完成 + 片头动画设计中**  
**日期：2026-05-14**

| 模块 | 状态 | 位置 |
|------|:--:|------|
| 产品策划 | ✅ 完整 | 用户文档 |
| 源数据库 | ✅ ~100 源，24 Gold + 1 太空必选 | `earth-sources/sources.yaml` |
| 健康检查 | ✅ 可运行 | `earth-sources/health_check.py` |
| 抓取管线 | ✅ yt-dlp 验证通过 | `/tmp/earth-test/` |
| 视频渲染 | ✅ 管线完成 | `earth-composite.py` |
| 渲染设计 | ✅ 已完成 | 白色Header + 深色InfoBar + Slogan |
| 片头动画 | 🔄 方案确定（Blender预渲染复用） | 待实现 |
| 太空源 | ✅ NASA ISS 已入库 mandatory | `sources.yaml` #14-27 |
| 版权确认 | ✅ 今日地球不侵权 | 引用注明灵感来源 |
| 竖屏版本 | ❌ 未开始 | — |
| 天气 API | ❌ 未开始 | — |
| 官网 | ❌ 未开始 | — |
| 自动化调度 | ⚠️ 会话级 cron | 需迁移到 Windows Task Scheduler |

---

## 核心管线（已验证）

```
 sources.yaml          health_check.py
      │                      │
      ▼                      ▼
  NASA ISS(必选) + 随机 4 源 ← 自动健康检查（可定时）
      │
      ▼
 yt-dlp 抓取 5-6s 片段（每个源，固定机位）
      │
      ▼
 FFmpeg 渲染叠加（每个片段）：
   ├── 白色 Header（「今日地球」+ 日期）
   ├── 16:9 视频画面居中
   ├── 深色 InfoBar（城市·国家 + 天气图标 + 温度 + 湿度 + 当地时间）
   └── 底部 Slogan（「把世界重新打开给下一代」）
      │
      ▼
 [片头 intro.mp4] → concat ← [片段1] [片段2] [片段3] [片段4] [片段5(太空)]
      │
      ▼
 成品：片头(3s) + 5片段(5-6s each) ≈ 28-33s 横屏 1920×1080
      │
      (待做) → 竖屏 1080×1920 + 封面图 + 上传存储
```

## 渲染设计规范

基于 GPT Mockup 确认，2026-05-14。

### 布局（1920×1080）
```
┌──────────────────────────────────────────┐
│  [今日地球·Logo]       2026/05/14 周二   │  白色Header (0-120px)
├──────────────────────────────────────────┤
│              (暖金色分割线 2px)           │
│                                          │
│           ┌──────────────────┐           │  视频画面 (140-880px)
│           │   城市实景画面    │           │  16:9, 居中, 留边距
│           │  (固定机位5-6s)  │           │  固定机位, 不摇摆
│           │                  │           │
│           └──────────────────┘           │
│                                          │
├──────────────────────────────────────────┤
│  城市名, 国家                            │  深色InfoBar (890-990px)
│  🌤 23°C    湿度 72%    当地时间 14:30  │  白色文字
│                                          │
│  今日地球 · 把世界重新打开给下一代      │  Slogan (1000-1060px)
└──────────────────────────────────────────┘
```

### 片段参数
| 参数 | 值 | 理由 |
|------|:--:|------|
| 每段时长 | 5-6s | 固定机位不需要太长，镜头本身不动 |
| 每期段数 | 5 段 | 覆盖不同大洲/场景 |
| 成品时长 | ~30s | 适合短视频平台 |
| 过渡方式 | 硬切+短暂黑场 | 简单干净，不抢画面 |

### Snowball 效应（未来）
- 真实天气 API 接入 → `🌤 23°C` 变成实时数据
- 相机机位信息 → 如果能获取 PTZ 状态，在 InfoBar 标注「固定/移动」
- 竖屏版本 → 背景虚化 + 横屏居中

---

## 源数据库

### 当前覆盖

```
亚洲 (6)：  东京×2，上海，曼谷，苏梅岛，杜拜
欧洲 (6)：  都柏林，伦敦，威尼斯×2，瑞士阿尔卑斯，格里门茨
北美 (4)：  迈阿密水下，檀香山，新奥尔良，洛杉矶 Venice Beach
南美 (1)：  里约热内卢 Copacabana
非洲 (2)：  开普敦，纳米布沙漠
大洋洲 (1)：悉尼港
─────────────────────────────
总计 20 个源，80% 在线率
```

### 场景分布

| 场景 | 数量 | 示例 |
|------|:--:|------|
| 城市 | 9 | Dublin, London, Tokyo, Venice, Shanghai, Bangkok... |
| 海滩 | 4 | Honolulu, LA, Koh Samui, Cape Town |
| 山地 | 2 | Swiss Alps, Grimentz |
| 水下 | 1 | Miami Coral City |
| 沙漠 | 1 | Namibia |
| 港湾 | 1 | Sydney Harbour |

### 仍需扩充

- 南美：Buenos Aires, Santiago
- 中东：Istanbul, Jerusalem
- 东亚：Seoul, Taipei, Singapore
- 欧洲：Paris, Berlin, Barcelona
- 机场/交通场景

---

## 技术踩坑记录

在 Windows 上跑 FFmpeg + 中文叠加遇到的坑：

| 坑 | 原因 | 解决 |
|----|------|------|
| `C:` 冒号被当 FFmpeg 分隔符 | 绝对路径含 `:` | `os.chdir()` + 相对路径 |
| 命令行中文被 GBK 破坏 | Windows 命令行编码 | `PYTHONUTF8=1` + `# -*- coding: utf-8 -*-` |
| `%` 被 FFmpeg drawtext 当转义符 | `72%` 中的 `%` | 改为 `RH72` 或 `72pct` |
| filter 链太长 | 多个 drawtext 串接 | 分步渲染，每步一个 drawtext |
| filter_script 不支持多行 | FFmpeg 文件格式 | 用逗号连成一行 |
| 空缓存文件 | 上次失败残留 | 健康检查验证文件大小 |

---

## 关键文件

| 文件 | 说明 |
|------|------|
| `C:\Users\Administrator\earth-sources\sources.yaml` | 源数据库 |
| `C:\Users\Administrator\earth-sources\health_check.py` | 健康检查脚本 |
| `C:\Users\Administrator\earth-composite.py` | 视频渲染脚本（上次运行） |
| `C:\Users\Administrator\Desktop\新建文本文档 (12).txt` | 原始产品策划文档 |
| `/tmp/earth-test/Today_on_Earth_demo.mp4` | 上次生成的成品视频 |

---

## 片头动画

**方案：Blender 预渲染 → 一次性出片 → 每天复用拼接**

- 3秒片头：地球自转 + 镜头推进 + 「今日地球」优雅淡入
- Blender Eevee 渲染，1920×1080@30fps，广播级画质
- 渲染一次产出 `intro.mp4`，存到 `C:/tmp/earth-render/`
- 每天 `earth-composite.py` 在 concat 阶段自动拼到最前面
- NASA Blue Marble 公共领域地球纹理（NASA Goddard Space Flight Center）

**依赖：** Blender (~300MB), Python bpy API, FFmpeg

---

## 版权分析

**结论：「今日地球」不侵权。**

| 层面 | 分析 |
|------|------|
| 商标 | "瞬间看地球"是 TVB Pearl 为 earthTV《Earth Live》起的译名。我们使用原创名「今日地球」，不构成商标侵权 |
| 著作权 | 节目名称太短，不受著作权保护 |
| 引用 | 底部 `Inspired by earthTV®` 小字属于合理致敬，不侵权 |
| 注意 | 不要在视频标题/封面直接使用"瞬间看地球"作为栏目名 |

---

## 太空源

| 源 | URL | 详情 |
|------|------|------|
| **NASA ISS 官方** | `https://www.youtube.com/watch?v=uwXgcTc8oY8` | NASA 频道 14.9M 订阅，is_live，1280×720@60fps，公共领域无版权 |
| Sen 4K | `https://www.youtube.com/watch?v=fO9e9jnhYK8` | 备选，4K Earth |
| Dream Trips | `https://www.youtube.com/watch?v=0FBiyFpV__g` | 备选 |
| The Launch Pad | `https://www.youtube.com/watch?v=t8B3ACpcNfc` | 备选 |

NASA ISS 已设为 `mandatory: true`，每次视频必选。

---

## 下一步

1. **片头动画** — Blender 安装 + render_intro.py + 渲染 intro.mp4
2. **修改 earth-composite.py** — 支持 mandatory 源 + 拼接片头
3. **首轮生产测试** — 完整跑一次管线验证质量
4. **定时巡检** — health_check.py 接入 Windows Task Scheduler，每 6 小时
5. **扩充源** — 补南美、中东、欧洲空缺
6. **天气 API** — OpenWeatherMap 接入真实数据
7. **竖屏版本** — FFmpeg 背景虚化 + 横屏居中
8. **官网 MVP** — Next.js + Supabase，首页 + 历史

---

## 产品初心

> 如果说在我心里排第一的电视节目，那一定是《瞬间看地球》。  
> 它曾经用音乐、画面和视角，培养了我对世界的好奇、审美和看待世界的方式。  
> 后来它停播了。这个世界上，也就少了一个无法替代的窗口。  
> 如果没有这样的环境，那就创造一个。

**品牌使命：把看世界的窗口，重新打开给下一代。**
