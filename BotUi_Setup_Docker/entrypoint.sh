#!/bin/bash
set -e

echo ""
echo "====================================="
echo "🧠 BotUI — Inicializando Container"
echo "====================================="

echo ""
echo "📦 Ambiente pronto!"
echo "➡️  Python: $(python3 --version 2>/dev/null || echo '❌ não encontrado')"

echo ""
echo "🖥️  Iniciando Xvfb em :99"
echo ""

# ================================
# 🔥 Xvfb REAL (não xvfb-run)
# ================================
Xvfb :99 -screen 0 1920x1080x24 &

export DISPLAY=:99

# Pequeno delay para garantir que o X server subiu
sleep 1

# ================================
# 🧪 Teus testes de ambiente (SEGUROS agora)
# ================================
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    browser.close()
print("✅ Playwright OK com Xvfb real")
EOF

echo ""
echo "====================================="
echo "🚀 Executando comando principal"
echo "====================================="
echo ""

# ================================
# 🚀 Executa o comando real
# ================================
exec "$@"
