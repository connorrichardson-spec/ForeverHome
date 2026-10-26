#!/usr/bin/env bash
# Run the walkthrough locally, rendering on the NVIDIA GPU when there is one.
# Usage: ./run-local.sh        (Ctrl+C to stop)   PORT=9000 ./run-local.sh to change the port
#        ./run-local.sh --live  open the published GitHub Pages site instead (no local server)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8000}"
LIVE_URL="https://connorrichardson-spec.github.io/ForeverHome/"

if [[ "${1:-}" == "--live" ]]; then
  URL="$LIVE_URL"
else
  URL="http://localhost:$PORT/"
  # serve web/ plus the exports (same layout as the GitHub Pages site)
  SITE="$(mktemp -d)"
  ln -s "$ROOT"/web/* "$SITE"/ && ln -s "$ROOT/exports" "$SITE/exports"
  python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$SITE" >/dev/null 2>&1 &
  SERVER=$!
  trap 'kill $SERVER 2>/dev/null; rm -rf "$SITE"' EXIT
  sleep 0.5
fi

# hybrid Intel+NVIDIA laptops: ask for the NVIDIA GPU (PRIME render offload)
if command -v nvidia-smi >/dev/null 2>&1; then
  export __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia
fi

# A separate Firefox instance + profile, so it starts on the NVIDIA GPU even if Firefox is already
# open (an existing Firefox keeps the GPU it started with).
PROFILE="$ROOT/.browser-profile"
mkdir -p "$PROFILE"
cat > "$PROFILE/user.js" <<'PREFS'
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("webgl.force-enabled", true);
PREFS
firefox --new-instance --profile "$PROFILE" "$URL" >/dev/null 2>&1 &

if [[ -n "${SERVER:-}" ]]; then
  echo "Walkthrough running at $URL  (Ctrl+C to stop)"
  wait $SERVER
else
  echo "Opened $URL on the NVIDIA GPU"
fi
