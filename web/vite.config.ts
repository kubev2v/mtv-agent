import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    target: "es2021",
    rollupOptions: {
      output: {
        manualChunks: {
              lit: ["lit"],
              markdown: ["marked", "marked-highlight", "dompurify"],
          hljs: ["highlight.js/lib/core"],
        },
      },
    },
  },
});
