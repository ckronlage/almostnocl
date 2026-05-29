#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_FILE="$ROOT_DIR/shared/niivue_assets/niivue.webgl2.single.min.js"
TMP_DIR="$(mktemp -d /tmp/niivue-mono-XXXXXX)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "[1/4] Cloning niivue/mono into $TMP_DIR"
git clone --depth 1 https://github.com/niivue/mono "$TMP_DIR"

echo "[2/4] Building @niivue/niivue dist with Dockerized Bun"
docker run --rm \
  -v "$TMP_DIR":/work \
  -w /work/packages/niivue \
  oven/bun:1 \
  sh -lc "bun install && bun run build"

echo "[3/4] Bundling into a single local WebGL2 file"
docker run --rm \
  -v "$ROOT_DIR":/workspace \
  -v "$TMP_DIR":/src \
  node:20 \
  sh -lc "mkdir -p /tmp/niivue-bundle && cd /tmp/niivue-bundle && npm init -y >/dev/null && npm install --silent esbuild gl-matrix nifti-reader-js cbor-x earcut clipper2-ts && NODE_PATH=/tmp/niivue-bundle/node_modules npx esbuild /src/packages/niivue/dist/niivuegpu.webgl2.js --bundle --format=esm --minify --outfile=/workspace/shared/niivue_assets/niivue.webgl2.single.min.js"

echo "[4/4] Done"
ls -lh "$OUT_FILE"
