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
        manualChunks(id) {
          if (id.includes("node_modules/lit")) return "lit";
          if (
            id.includes("node_modules/marked") ||
            id.includes("node_modules/dompurify")
          )
            return "markdown";
          if (id.includes("node_modules/highlight.js")) return "hljs";
        },
      },
    },
  },
});
