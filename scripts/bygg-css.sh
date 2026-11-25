#!/usr/bin/env sh
# Bygger static/css/app.css fra static/css/input.css med Tailwind v4 frittstående CLI.
# Binæren hentes fra TAILWIND_BIN, eller fra PATH som `tailwindcss`. Den committes ikke.
set -e
ROT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="${TAILWIND_BIN:-tailwindcss}"
command -v "$BIN" >/dev/null 2>&1 || { echo "Tailwind-CLI finnes ikke: $BIN. Sett TAILWIND_BIN." >&2; exit 1; }
"$BIN" -i "$ROT/static/css/input.css" -o "$ROT/static/css/app.css" --minify
