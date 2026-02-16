export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      // Добавляем новый брейкпоинт
      screens: {
        'pc': '829px', 
      },
      colors: {
        dark: { 400: '#818181', 500: '#666666', 600: '#515151', 700: '#434343', 800: '#383838', 900: '#121212', 950: '#0a0a0a' },
        accent: { green: '#4ade80', cyan: '#22d3ee', red: '#ef4444' }
      },
      fontFamily: { 
        display: ['DrukWideCyr', 'sans-serif'], 
        sans: ['Golos-Regular', 'system-ui', 'sans-serif'] 
      }
    }
  },
  plugins: []
};