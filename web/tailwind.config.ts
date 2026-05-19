import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark Minimal + Pale Blue Earth Signal
        "earth-900": "#0a0a0f", // page background
        "earth-800": "#12121a", // card/panel
        "earth-700": "#1e1e2e", // dividers
        "earth-600": "#2a2a3a", // hover states
        "earth-300": "#8888a0", // secondary text
        "earth-100": "#e8e8ed", // primary text
        "earth-blue": "#5b9bd5", // pale blue earth signal
        "earth-gold": "#d4b872", // warm gold accent
      },
      fontFamily: {
        serif: ["var(--font-serif)", "serif"],
        sans: ["var(--font-sans)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      maxWidth: {
        "8xl": "1280px",
      },
    },
  },
  plugins: [],
};
export default config;
