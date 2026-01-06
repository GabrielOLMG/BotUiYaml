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
echo "🖥️ Verificando DISPLAY..."

if [ -z "$DISPLAY" ]; then
    echo "➡️  DISPLAY não definido, iniciando Xvfb em :99"
    export DISPLAY=:99

    Xvfb :99 -screen 0 1920x1080x24 -ac +extension RANDR &
    XVFB_PID=$!

    # garante shutdown limpo
    trap "echo '🧹 Encerrando Xvfb'; kill $XVFB_PID" EXIT

    # espera subir
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
else
    echo "✅ DISPLAY já ativo ($DISPLAY)"
fi


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
