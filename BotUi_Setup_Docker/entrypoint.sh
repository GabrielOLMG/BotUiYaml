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
echo "➡️  Chromium: $(chromium --version 2>/dev/null || echo '❌ não encontrado')"
echo "➡️  ChromeDriver: $(chromedriver --version 2>/dev/null || echo '❌ não encontrado')"
echo ""
echo "====================================="

# =====================================
# 🚀 Executa o comando principal
# =====================================
exec "$@"
