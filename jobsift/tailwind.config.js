/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './templates/*.html',
    './*/*.html',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {},
    spacing: {
      '1': '0.25rem',
      '2': '0.5rem',
      '3': '0.75rem',
      '4': '1rem',
      '5': '1.25rem',
      '6': '1.5rem',
      '8': '2rem',
      '10': '2.5rem',
      // ...
    },
  },
  plugins: [
    require('flowbite/plugin')
  ],
}

