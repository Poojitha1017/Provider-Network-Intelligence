/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#0a1628",
          900: "#0f1f38",
          850: "#132548",
          800: "#182d54",
          700: "#1f3a6b",
          600: "#2b4c85",
        },
        brand: {
          50: "#eef4ff",
          100: "#dce8ff",
          200: "#b8d1ff",
          300: "#8ab3ff",
          400: "#548dfa",
          500: "#2f6ce8",
          600: "#1f52c4",
          700: "#1a419e",
          800: "#183880",
          900: "#173169",
        },
        risk: {
          low: "#16a34a",
          lowbg: "#dcfce7",
          medium: "#d97706",
          mediumbg: "#fef3c7",
          high: "#ea580c",
          highbg: "#ffedd5",
          critical: "#dc2626",
          criticalbg: "#fee2e2",
        },
        surface: {
          DEFAULT: "#f6f8fb",
          card: "#ffffff",
          border: "#e4e9f2",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 31, 56, 0.06), 0 1px 6px rgba(15, 31, 56, 0.05)",
        popover: "0 8px 30px rgba(15, 31, 56, 0.18)",
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.1rem",
      },
    },
  },
  plugins: [],
};
