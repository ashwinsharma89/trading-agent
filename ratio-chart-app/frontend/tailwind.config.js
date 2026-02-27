/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // TradingView dark palette
        background: '#0d1117',
        surface:    '#131722',
        surface2:   '#1e222d',
        border:     '#2a2e39',
        text:       '#d1d4dc',
        'text-secondary': '#787b86',
        green:      '#26a69a',
        red:        '#ef5350',
        yellow:     '#f7c948',
        blue:       '#2962ff',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
