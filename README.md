# Today on Earth / 今日地球

> 每天两次，随机看看此刻的地球。  
> Reopen a window for seeing the world.

---

## 项目结构

```
today-on-earth/
├── pipeline/          ← 视频生产管线（Python + FFmpeg）
│   ├── sources.yaml          源数据库（~100 个全球公开影像源）
│   ├── health_check.py       源健康检查
│   ├── earth-composite.py    视频合成渲染
│   ├── scrape_skyline.py     抓取脚本
│   ├── render_intro.py       片头渲染
│   ├── convert_to_mp4.py     格式转换
│   └── PROJECT.md            管线详细文档
│
├── web/               ← 展示网站（Next.js + Supabase）
│   ├── app/                  Next.js App Router 页面
│   ├── components/           UI 组件
│   ├── lib/                  工具库
│   └── README.md            网站开发文档
│
└── README.md          ← 本文件
```

## 工作流程

```
sources.yaml → health_check.py → yt-dlp 抓取 → FFmpeg 渲染 → .mp4 成品
                                                              │
                                              Supabase Storage ← 上传
                                                              │
                                              Next.js 网站 ← 播放
```

## 快速开始

### 管线（视频生成）

```bash
cd pipeline
python health_check.py           # 检查源状态
python earth-composite.py        # 生成今日视频
```

### 网站（前端）

```bash
cd web
npm install
npm run dev                      # 本地开发 → http://localhost:3000
```

## MVP 状态（2026-05-19）

| 模块 | 状态 |
|------|:--:|
| 源数据库 | ✅ ~100 源，24 Gold |
| 健康检查 | ✅ |
| 视频渲染管线 | ✅ |
| 片头动画 | 🔄 方案已定 |
| 网站前端 | ✅ 完成 |
| 数据库 (Supabase) | ⚠️ 需配置 |
| 部署 (Vercel) | ⚠️ 需配置 |
| 天气 API | ❌ 未开始 |
| 竖屏版本 | ❌ 未开始 |
| 自动化调度 | ⚠️ 开发中 |

## 核心理念

不是新闻，不是旅游广告，不是短视频。

只是一个每天两次让你看见地球另一边的窗口。

**如果没有这样的环境，那就创造一个。**

---

Inspired by earthTV®
