/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          bg: "#090A0F",
          card: "#11131E",
          border: "#1E2235",
          muted: "#6B7280",
          text: "#F3F4F6",
        },
        brand: {
          primary: "#8B5CF6",    // Electric Violet
          secondary: "#06B6D4",  // Neon Cyan
          accent: "#EC4899",     // Hot Pink
          success: "#10B981",    // Emerald
          warning: "#F59E0B",    // Amber
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'neon-purple': '0 0 15px rgba(139, 92, 246, 0.45)',
        'neon-cyan': '0 0 15px rgba(6, 182, 212, 0.45)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}
