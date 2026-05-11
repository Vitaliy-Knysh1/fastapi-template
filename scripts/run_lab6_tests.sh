#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT_DIR="$ROOT/docs/lab6"
mkdir -p "$OUT_DIR"

echo "Lab 6: API tests (PostgreSQL must be reachable; database app_test is created if missing)"
echo "Root: $ROOT"
echo ""

poetry run pytest tests/ -v --tb=short \
  --html="$OUT_DIR/pytest_report.html" \
  --self-contained-html \
  2>&1 | tee "$OUT_DIR/pytest_output.txt"

echo ""
echo "HTML report: $OUT_DIR/pytest_report.html"
echo "Console log: $OUT_DIR/pytest_output.txt"
