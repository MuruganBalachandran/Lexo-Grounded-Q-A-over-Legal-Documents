/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        surface: 'var(--surface)',
        surfaceMuted: 'var(--surfaceMuted)',
        ink: 'var(--ink)',
        inkSecondary: 'var(--inkSecondary)',
        border: 'var(--border)',
        accent: 'var(--accent)',
        accentMuted: 'var(--accentMuted)',
        citation: 'var(--citation)',
        citationMuted: 'var(--citationMuted)',
        refuse: 'var(--refuse)',
        refuseMuted: 'var(--refuseMuted)',
      },
      fontFamily: {
        serif: ['var(--font-display)', 'serif'],
        sans: ['var(--font-body)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
    },
  },
  plugins: [],
}
