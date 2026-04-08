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
        spectre: {
          bg: '#080B14',
          surface: '#0D1117',
          card: '#131920',
          border: '#1E2A3A',
          borderLight: '#2A3A4E',
          text: '#E6EDF3',
          textMuted: '#7D8590',
          textDim: '#484F58',
          accent: '#00F5D4',
          accentDim: '#00C4A7',
          accentGlow: 'rgba(0, 245, 212, 0.15)',
          warning: '#FFB347',
          danger: '#FF6B6B',
          success: '#2ECC71',
          purple: '#9B59B6',
          pink: '#FF69B4',
          cyan: '#00BCD4',
          magenta: '#E91E63',
        },
        tamper: {
          copyPaste: '#FF4444',
          overwrite: '#F1C40F',
          addedContent: '#FF8C00',
          erasure: '#3498DB',
          merged: '#E91E63',
          watermark: '#2ECC71',
          spacing: '#00BCD4',
          aiGenerated: '#9B59B6',
          aiEdit: '#FF69B4',
        }
      },
      fontFamily: {
        heading: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'scan': 'scan 2.5s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
        'bbox-pulse': 'bboxPulse 1.5s ease-in-out infinite',
      },
      keyframes: {
        scan: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '10%': { opacity: '1' },
          '90%': { opacity: '1' },
          '100%': { transform: 'translateY(100%)', opacity: '0' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(0, 245, 212, 0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(0, 245, 212, 0.6)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideRight: {
          '0%': { opacity: '0', transform: 'translateX(-16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        bboxPulse: {
          '0%, 100%': { opacity: '0.7' },
          '50%': { opacity: '1' },
        },
      },
      boxShadow: {
        'glow': '0 0 15px rgba(0, 245, 212, 0.3)',
        'glow-lg': '0 0 30px rgba(0, 245, 212, 0.4)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.4)',
      },
    },
  },
  plugins: [],
}
