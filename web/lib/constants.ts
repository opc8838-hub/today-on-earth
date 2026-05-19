// Today on Earth — Design Tokens & Constants

export const COLORS = {
  page: "#0a0a0f",
  card: "#12121a",
  divider: "#1e1e2e",
  hover: "#2a2a3a",
  textSecondary: "#8888a0",
  textPrimary: "#e8e8ed",
  earthBlue: "#5b9bd5",
  earthGold: "#d4b872",
} as const;

export const SITE = {
  name: "Today on Earth",
  nameCN: "今日地球",
  slogan: "每天两次，随机看看此刻的地球",
  mission: "把世界重新打开给下一代",
  missionEN: "Reopen a window for seeing the world, especially for the next generation.",
  description:
    "Today on Earth 是一个每天自动生成的全球实时影像栏目。每天早上和下午，从世界不同国家与地区的公开视频源中，选取正在发生的真实片段，生成短视频。它不是新闻，也不是旅游广告。它只是想让你在一天之中，有两个瞬间，看见地球的另一边正在发生什么。",
} as const;

export const NAV_LINKS = [
  { href: "/", label: "Home", labelCN: "首页" },
  { href: "/archive", label: "Archive", labelCN: "历史" },
  { href: "/about", label: "About", labelCN: "关于" },
] as const;
