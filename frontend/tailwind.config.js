/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        // Palette verte naturelle et locale
        nature: {
          50: '#f7faf5',
          100: '#eef5e8',
          200: '#ddebd1',
          300: '#c4dbb0',
          400: '#a8c789',
          500: '#8fb368',
          600: '#6f9a4a',
          700: '#567a3a',
          800: '#466130',
          900: '#3b5029',
        },
        earth: {
          50: '#faf8f5',
          100: '#f5f0e8',
          200: '#e8dcc8',
          300: '#d4c2a0',
          400: '#b8a078',
          500: '#9d8258',
          600: '#7d6846',
          700: '#645139',
          800: '#524330',
          900: '#45382a',
        },
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
        '4xl': '2.5rem',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '26': '6.5rem',
        '30': '7.5rem',
      },
      boxShadow: {
        'nature': '0 4px 14px 0 rgba(111, 154, 74, 0.15)',
        'nature-lg': '0 10px 25px -3px rgba(111, 154, 74, 0.2)',
      },
    },
  },
  plugins: [],
}

