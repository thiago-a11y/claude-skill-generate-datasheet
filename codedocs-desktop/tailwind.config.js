/** @type {import('tailwindcss').Config} */
export default {
  content: ["src/**/*.{tsx,ts,html}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0f",
        bg2: "#12121a",
        bg3: "#1a1a2e",
        fg: "#e0e0e8",
        fg2: "#a0a0b0",
        accent: "#f59e0b",
        accent2: "#3b82f6",
      },
    },
  },
  plugins: [],
};
