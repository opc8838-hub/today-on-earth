import { Metadata } from "next";
import { SITE } from "@/lib/constants";

export const metadata: Metadata = {
  title: "About",
};

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-24">
      {/* Hero */}
      <section className="mb-20">
        <h1 className="text-3xl font-serif font-bold text-earth-100 mb-6 tracking-wide">
          {SITE.slogan}
        </h1>
        <div className="w-12 h-px bg-earth-blue mb-8" />
        <p className="text-lg text-earth-300 leading-relaxed">
          Today on Earth / 今日地球，是一个每天自动生成的全球实时影像栏目。
        </p>
      </section>

      {/* Mission */}
      <section className="mb-20">
        <p className="text-earth-300 leading-relaxed mb-6">
          我们每天早上和下午，从世界不同国家与地区的公开视频源中，选取正在发生的真实片段，生成一条 15–30 秒的短视频。
        </p>
        <p className="text-earth-300 leading-relaxed mb-6">
          它不是新闻，也不是旅游广告。
        </p>
        <p className="text-earth-300 leading-relaxed mb-6">
          它只是想让你在一天之中，有两个瞬间，看见地球的另一边正在发生什么。
        </p>
        <p className="text-earth-100 leading-relaxed text-lg font-medium">
          世界很大，而我们值得从小拥有看世界的视角。
        </p>
      </section>

      {/* Mission statement */}
      <section className="mb-20">
        <div className="border-l-2 border-earth-blue pl-6 py-2">
          <p className="text-xl font-serif text-earth-100 leading-relaxed">
            {SITE.mission}
          </p>
          <p className="text-earth-300 mt-3">{SITE.missionEN}</p>
        </div>
      </section>

      {/* Origin */}
      <section className="mb-20">
        <h2 className="text-sm tracking-widest uppercase text-earth-blue mb-6">
          Origin / 起源
        </h2>
        <p className="text-earth-300 leading-relaxed mb-4">
          这个项目的灵感来源，是一档经典的电视节目——它曾经用音乐、画面和视角，培养了一代人对世界的好奇、审美和看待世界的方式。
        </p>
        <p className="text-earth-300 leading-relaxed mb-4">
          后来它停播了。这个世界上，也就少了一个无法替代的窗口。
        </p>
        <p className="text-earth-100 leading-relaxed font-medium">
          如果没有这样的环境，那就创造一个。
        </p>
      </section>

      {/* Tech */}
      <section className="mb-20">
        <h2 className="text-sm tracking-widest uppercase text-earth-blue mb-6">
          Technology / 技术
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[
            "Next.js",
            "Tailwind CSS",
            "Supabase",
            "FFmpeg",
            "yt-dlp",
            "Python",
            "Vercel",
            "YouTube Live",
            "NASA ISS",
          ].map((tech) => (
            <div
              key={tech}
              className="px-4 py-2 rounded-md bg-earth-800 border border-earth-700 text-xs text-earth-300 text-center"
            >
              {tech}
            </div>
          ))}
        </div>
      </section>

      {/* Credits */}
      <section>
        <h2 className="text-sm tracking-widest uppercase text-earth-blue mb-6">
          Credits / 致敬
        </h2>
        <p className="text-xs text-earth-600 leading-relaxed">
          Inspired by earthTV&reg; and the classic TV program that opened windows
          to the world. All video footage comes from public sources including
          YouTube Live streams, NASA ISS public domain imagery, and public city
          cameras. No copyrighted content is used without attribution.
        </p>
      </section>
    </div>
  );
}
