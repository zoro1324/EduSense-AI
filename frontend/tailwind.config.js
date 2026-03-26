/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0f172a',
        card: '#1e293b',
        border: '#334155',
        text: '#f1f5f9',
        muted: '#94a3b8',
        primary: '#6366f1',
        secondary: '#818cf8',
        success: '#22c55e',
        warning: '#eab308',
        danger: '#ef4444',
        dark: '#0f172a',
      },
      boxShadow: {
        card: '0 10px 24px -8px rgba(15, 23, 42, 0.45)',
        hover: '0 18px 30px -12px rgba(15, 23, 42, 0.6)',
      }
    },
  },
  plugins: [],
}
