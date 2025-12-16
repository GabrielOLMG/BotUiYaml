#!/bin/bash
set -e

echo ""
echo "====================================="
echo "🧠 BotUI — Inicializando Container"
echo "====================================="

# =====================================
# 🧩 Diagnóstico do ambiente
# =====================================
echo ""
echo "📦 Ambiente pronto!"
echo "➡️  Python: $(python3 --version 2>/dev/null || echo '❌ não encontrado')"

# -------------------------------------
# 🧪 Teste rápido do Playwright
# -------------------------------------
echo -n "➡️  Playwright: "
python3 - <<'EOF'
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        browser.close()
    print("✅ OK")
except Exception as e:
    print("❌ ERRO")
    raise
EOF

echo ""
echo "====================================="

# =====================================
# 🚀 Executa o comando principal
# =====================================
exec "$@"
