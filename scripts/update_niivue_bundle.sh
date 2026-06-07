#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_FILE="$ROOT_DIR/shared/niivue_assets/niivue.webgl2.single.min.js"
echo "[1/2] Bundling @niivue/niivue@0.69.0 into a single local WebGL2 file"
docker run --rm \
  -v "$ROOT_DIR":/workspace \
  node:20 \
  sh -lc "mkdir -p /tmp/niivue-bundle && cd /tmp/niivue-bundle && npm init -y >/dev/null && npm install --silent esbuild @niivue/niivue@0.69.0 && npx esbuild node_modules/@niivue/niivue/build/niivue/index.js --bundle --format=esm --platform=browser --minify --outfile=/workspace/shared/niivue_assets/niivue.webgl2.single.min.js"

echo "[2/2] Done"
ls -lh "$OUT_FILE"
