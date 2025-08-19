import { defineConfig, Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { addImportPrefix } from "imports-prefix-vite-plugin";
import path from "path";
import { fileURLToPath } from "url";

// Get current directory in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    addImportPrefix({
      prefix: "/routelit/routelit_mantine/",
    }) as Plugin,
  ],
  define: {
    // Provide polyfill for process.env
    "process.env": {},
  },
  build: {
    outDir: "../routelit_mantine/static",
    emptyOutDir: true,
    manifest: true,
    lib: {
      entry: path.resolve(__dirname, "src/index.ts"),
      name: "RoutelitMantine",
      fileName: (format) => `routelit-mantine.${format}.js`,
      formats: ["es"], // Only using ES modules for consistency
    },
    rollupOptions: {
      external: ["react", "react-dom", "react/jsx-runtime", "routelit-client"],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
          "react/jsx-runtime": "jsxRuntime",
          "routelit-client": "RoutelitClient",
        },
      },
    },
    minify: true,
    sourcemap: true,
  },
});
