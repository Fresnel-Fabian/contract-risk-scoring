/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        void:    '#050C1A',
        ink:     '#0A1628',
        surface: '#0F1E35',
        panel:   '#162440',
        edge:    '#1E3050',
        muted:   '#2A4060',
        amber:   '#C9933A',
        amber2:  '#E8AD50',
        amber3:  '#F5C96A',
        cream:   '#F5EDD6',
        slate:   '#8CA0BB',
        fog:     '#B8CCDF',
        urgent:  '#C0392B',
        flag:    '#B87332',
        clear:   '#1E6B40',
      },
      fontFamily: {
        display: ['var(--font-playfair)', 'Georgia', 'serif'],
        body:    ['var(--font-source)',   'Georgia', 'serif'],
        mono:    ['var(--font-ibm)',      'Courier New', 'monospace'],
      },
      animation: {
        'gauge-fill':   'gaugeFill 1.4s cubic-bezier(0.34,1.56,0.64,1) forwards',
        'fade-up':      'fadeUp 0.6s ease forwards',
        'shimmer':      'shimmer 2s infinite',
        'pulse-amber':  'pulseAmber 2s ease-in-out infinite',
      },
      keyframes: {
        gaugeFill: {
          '0%':   { strokeDashoffset: '283' },
          '100%': { strokeDashoffset: 'var(--target-offset)' },
        },
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        },
        pulseAmber: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.5' },
        },
      },
    },
  },
  plugins: [],
}
