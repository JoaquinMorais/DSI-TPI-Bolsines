/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f4f7f9",
          100: "#e7edf2",
          200: "#cbd8e1",
          300: "#a6bccb",
          400: "#7a9ab0",
          500: "#587e97",
          600: "#45647b",
          700: "#395164",
          800: "#314554",
          900: "#0f2a43",
          950: "#081a2b",
        },
        brand: {
          50: "#effcf9",
          100: "#d7f7ef",
          200: "#b0eee0",
          300: "#7ddfcd",
          400: "#45c8b4",
          500: "#22ab99",
          600: "#16897d",
          700: "#0f766e",
          800: "#115e59",
          900: "#134e4a",
          950: "#052e2b",
        },
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(15 42 67 / 0.04), 0 8px 24px -12px rgb(15 42 67 / 0.12)",
        "card-hover":
          "0 4px 12px -2px rgb(15 42 67 / 0.08), 0 18px 40px -18px rgb(15 42 67 / 0.2)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 200ms ease-out both",
        "slide-up": "slide-up 250ms ease-out both",
      },
    },
  },
  plugins: [],
};
