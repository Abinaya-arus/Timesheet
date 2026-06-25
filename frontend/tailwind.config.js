/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        'bg-primary':   '#ffffff',
        'bg-secondary': '#f4f5f6',
        'bg-tertiary':  '#ebecee',
        'bg-info':      '#e6f1fb',
        'bg-success':   '#eaf3de',
        'text-primary':   '#171717',
        'text-secondary': '#6b7280',
        'text-tertiary':  '#9ca3af',
        'text-info':      '#185fa5',
        'text-success':   '#3b6d11',
        'border-secondary': '#d1d5db',
        'border-tertiary':  '#e5e7eb',
        'border-info':      '#378add',
      },
      borderRadius: {
        lg: '8px',
        md: '6px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'Avenir', 'Helvetica', 'Arial', 'sans-serif'],
      },
      fontSize: {
        '9':  ['9px',  { lineHeight: '1.4' }],
        '10': ['10px', { lineHeight: '1.4' }],
        '11': ['11px', { lineHeight: '1.4' }],
        '12': ['12px', { lineHeight: '1.5' }],
        '13': ['13px', { lineHeight: '1.5' }],
        '14': ['14px', { lineHeight: '1.5' }],
        '15': ['15px', { lineHeight: '1.5' }],
        '22': ['22px', { lineHeight: '1' }],
      },
    },
  },
  plugins: [],
}
