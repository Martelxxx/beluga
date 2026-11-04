#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$0")"
echo "Beluga Agent Runtime — macOS setup (read-only browser test)"
if [[ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]]; then
  source "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
fi
node_ok() {
  command -v node >/dev/null 2>&1 &&
  node -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit(a>22||(a===22&&b>=18)?0:1)'
}
if ! node_ok; then
  if command -v nvm >/dev/null 2>&1; then
    nvm install 22
    nvm use 22
  elif command -v brew >/dev/null 2>&1; then
    if brew list --versions node@22 2>/dev/null | grep -q node@22; then
      brew upgrade node@22 || true
    else
      brew install node@22
    fi
    export PATH="$(brew --prefix node@22)/bin:$PATH"
  else
    echo "Install Node.js 22.18+ from https://nodejs.org, then rerun."
    exit 1
  fi
fi
node_ok || { echo "Node.js version too old"; exit 1; }
node --version
if ! command -v browse >/dev/null 2>&1; then
  echo "Installing Browserbase browse CLI..."
  npm install -g browse@latest
else
  browse --version
fi
echo "Installing Stagehand dependencies..."
npm install --no-audit --no-fund
if [[ -z "${BROWSERBASE_API_KEY:-}" ]]; then
  printf 'Paste existing Browserbase API key (hidden): '
  IFS= read -r -s BROWSERBASE_API_KEY
  printf '\n'
  [[ -n "$BROWSERBASE_API_KEY" ]] || exit 1
  export BROWSERBASE_API_KEY
fi
echo "Verifying Browserbase access..."
browse cloud projects list
echo "Starting first read-only cloud session..."
node src/smoke.mjs https://example.com/
echo "Verifying sessions..."
browse cloud sessions list
echo "Running Beluga tests..."
npm test
echo "Completed. Review session at https://www.browserbase.com/sessions"
