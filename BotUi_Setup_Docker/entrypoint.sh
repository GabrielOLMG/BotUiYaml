#!/bin/bash
set -e

echo ""
echo "====================================="
echo "🧠 BotUI — Inicializando Container"
echo "====================================="

echo ""
echo "📦 Ambiente pronto!"
echo "➡️  Python: $(python3 --version 2>/dev/null || echo '❌ não encontrado')"

# ================================
# 🖥️ Inicializa Xvfb
# ================================
echo ""
echo "🖥️  Iniciando Xvfb em :99"

Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR &
XVFB_PID=$!

export DISPLAY=:99

# Garante shutdown limpo
trap "echo '🧹 Encerrando Xvfb'; kill $XVFB_PID" EXIT

# Espera Xvfb subir de verdade
for i in {1..10}; do
  if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "✅ Xvfb ativo"
    break
  fi
  sleep 0.3
done

if ! xdpyinfo -display :99 >/dev/null 2>&1; then
  echo "❌ Xvfb não iniciou corretamente"
  exit 1
fi

# ================================
# 🧪 Smoke test Playwright (rápido)
# ================================
echo ""
echo "🧪 Testando Playwright (smoke test)"

python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("about:blank")
    browser.close()
print("✅ Playwright OK")
EOF

# ================================
# 🚀 Execução principal
# ================================
echo ""
echo "====================================="
echo "🚀 Executando comando principal"
echo "====================================="
echo ""

exec "$@"
