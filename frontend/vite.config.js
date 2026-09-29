import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, API/admin calls go to Django on :8000. In production Django serves the build.
export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === "production" ? "/static/" : "/",
  server: {
    proxy: { "/api": "http://127.0.0.1:8000", "/admin": "http://127.0.0.1:8000", "/media": "http://127.0.0.1:8000" },
  },
});
