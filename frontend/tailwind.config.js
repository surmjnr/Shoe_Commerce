/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f8f7f4',
          100: '#efede6',
          200: '#ddd8cc',
          300: '#c4bba8',
          400: '#a89980',
          500: '#8f7d62',
          600: '#7a6a52',
          700: '#655644',
          800: '#544839',
          900: '#473d32',
          950: '#262018',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['DM Sans', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
