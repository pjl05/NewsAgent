/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'bg-deep': '#0a0a0f',
        'bg-surface': '#12121f',
        'bg-elevated': '#1a1a2e',
        'aurora-purple': '#6366f1',
        'aurora-blue': '#8b5cf6',
        'aurora-cyan': '#22d3ee',
        'accent-warm': '#f59e0b',
        'accent-rose': '#f43f5e',
        'text-primary': '#f1f5f9',
        'text-secondary': '#94a3b8',
        'text-muted': '#64748b',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'aurora-drift': 'aurora-drift 8s ease-in-out infinite alternate',
        'wave-rise': 'wave-rise 0.8s ease-in-out infinite alternate',
        'bubble-pop': 'bubble-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'player-slide-up': 'player-slide-up 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      keyframes: {
        'aurora-drift': {
          '0%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -40px) scale(1.05)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.95)' },
          '100%': { transform: 'translate(40px, 30px) scale(1.02)' },
        },
        'wave-rise': {
          '0%': { transform: 'scaleY(0.3)', opacity: '0.6' },
          '100%': { transform: 'scaleY(1)', opacity: '1' },
        },
        'bubble-pop': {
          '0%': { transform: 'scale(0.8)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'player-slide-up': {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
