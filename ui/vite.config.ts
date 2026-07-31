import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Frontend for the DJ Transition Analyzer.
// Runs standalone in the browser today; Tauri wraps this same build later
// (tauri.conf.json -> build.frontendDist = "../ui/dist").
export default defineConfig({
  root: ".",
  server: { port: 1420, strictPort: false },
  build: { outDir: "dist", target: "es2020" },
});
