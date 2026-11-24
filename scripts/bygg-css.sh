#!/usr/bin/env sh
# Bygger static/css/app.css fra static/css/input.css med Tailwind v4 frittstående CLI.
# Binæren hentes fra TAILWIND_BIN, eller fra PATH som `tailwindcss`. Den committes ikke.
set -e
ROT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="${TAILWIND_BIN:-tailwindcss}"
"$BIN" -i "$ROT/static/css/input.css" -o "$ROT/static/css/app.css" --minify
