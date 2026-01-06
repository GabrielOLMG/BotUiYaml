#!/bin/bash
set -e

echo ""
echo "====================================="
echo "🧠 BotUI — Inicializando Ambiente"
echo "====================================="

echo ""
echo "📦 Ambiente pronto!"
echo "➡️  Python: $(python3 --version 2>/dev/null || echo '❌ não encontrado')"

# --------------------------------------------------
# 🖥️ DISPLAY / XVFB
# --------------------------------------------------
echo ""
echo "🖥️ Preparando ambiente gráfico..."

XVFB_PID=""
CREATED_XVFB=0

if [ -z "$DISPLAY" ]; then
    export DISPLAY=:99

    # limpeza preventiva (segura)
    rm -f /tmp/.X99-lock
    rm -f /tmp/.X11-unix/X99 2>/dev/null || true

    echo "➡️  Iniciando Xvfb em $DISPLAY"
    Xvfb $DISPLAY -screen 0 1920x1080x24 -ac +extension RANDR &
    XVFB_PID=$!
    CREATED_XVFB=1

    # espera subir
    for i in {1..10}; do
        if xdpyinfo -display $DISPLAY >/dev/null 2>&1; then
            echo "✅ Xvfb ativo ($DISPLAY)"
            break
        fi
        sleep 0.3
    done

    if ! xdpyinfo -display $DISPLAY >/dev/null 2>&1; then
        echo "❌ Xvfb não iniciou corretamente"
        exit 1
    fi
else
    echo "✅ DISPLAY já definido ($DISPLAY)"
fi

# --------------------------------------------------
# 🧹 CLEANUP GARANTIDO
# --------------------------------------------------
cleanup() {
    if [ "$CREATED_XVFB" -eq 1 ]; then
        echo ""
        echo "🧹 Encerrando Xvfb ($DISPLAY)"
        kill $XVFB_PID 2>/dev/null || true
        rm -f /tmp/.X99-lock
        rm -f /tmp/.X11-unix/X99 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

# --------------------------------------------------
# 🧪 Smoke test Playwright
# --------------------------------------------------
echo ""
echo "🧪 Testando Playwright..."

python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("about:blank")
    browser.close()
print("✅ Playwright OK")
EOF

# --------------------------------------------------
# 🚀 Execução principal
# --------------------------------------------------
echo ""
echo "====================================="
echo "🚀 Executando comando:"
echo "➡️  $@"
echo "====================================="
echo ""

exec "$@"
