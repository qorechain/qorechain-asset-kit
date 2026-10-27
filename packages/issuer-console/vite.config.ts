// SPDX-License-Identifier: Apache-2.0
import { defineConfig, type Plugin } from "vitest/config";
import react from "@vitejs/plugin-react";

/**
 * Production builds carry a Content-Security-Policy that forbids every network connection from the page
 * (connect-src 'none'): reads and writes go through the wallet's injected provider only. Not applied to
 * the dev server, whose module reloading needs inline scripts and a websocket.
 */
function contentSecurityPolicy(): Plugin {
  const policy =
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'none'";
  return {
    name: "issuer-console-csp",
    apply: "build",
    transformIndexHtml: () => [
      { tag: "meta", attrs: { "http-equiv": "Content-Security-Policy", content: policy }, injectTo: "head-prepend" },
    ],
  };
}

export default defineConfig({
  plugins: [react(), contentSecurityPolicy()],
  // Relative asset URLs: the console can be served from any path of a static host.
  base: "./",
  build: {
    sourcemap: false,
    outDir: "dist",
    emptyOutDir: true,
    // One bundle of about 620 kB (viem and the CMTAT creation bytecode); no code splitting needed.
    chunkSizeWarningLimit: 800,
  },
  test: {
    include: ["src/**/*.test.ts"],
    environment: "node",
  },
});
