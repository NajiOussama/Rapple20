/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,jsx,ts,tsx}"], // ← ajoute jsx/tsx si tu es en React
  theme: {
    extend: {
      fontFamily: {
        tech: ['Orbitron', 'sans-serif'],
        console: ['Courier Prime', 'monospace'],
      },
    },
  },
  plugins: [],
};
