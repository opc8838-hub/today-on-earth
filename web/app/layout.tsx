import type { Metadata } from "next";
import NavBar from "@/components/layout/NavBar";
import Footer from "@/components/layout/Footer";
import { SITE } from "@/lib/constants";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: `${SITE.name} | ${SITE.nameCN}`,
    template: `%s | ${SITE.name}`,
  },
  description: SITE.description,
  keywords: ["earth", "live", "video", "global", "今日地球", "世界"],
  openGraph: {
    title: `${SITE.name} | ${SITE.nameCN}`,
    description: SITE.slogan,
    type: "website",
    locale: "zh_CN",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="antialiased min-h-screen flex flex-col bg-earth-900 text-earth-100">
        <NavBar />
        <main className="flex-1 pt-14">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
