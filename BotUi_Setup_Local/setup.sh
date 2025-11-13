#!/bin/bash
set -e

echo ""
echo "============================================="
echo "🤖 BotUI — Configuração Local (Sem Docker)"
echo "============================================="
echo ""

# ---------------------------------------------
# 1️⃣ Detecta ambiente
# ---------------------------------------------
if grep -qi microsoft /proc/version; then
    echo "💻 Ambiente detectado: WSL (Windows Subsystem for Linux)"
else
    echo "💻 Ambiente detectado: Linux nativo"
fi

# ---------------------------------------------
# 2️⃣ Atualiza lista de pacotes (sem upgrade)
# ---------------------------------------------
echo ""
echo "📦 Atualizando lista de pacotes..."
sudo apt-get update -y

# ---------------------------------------------
# 3️⃣ Instala dependências principais
# ---------------------------------------------
echo ""
echo "🔧 Instalando dependências principais..."

# Pacotes compatíveis com Ubuntu e Debian modernos (inclui fallback t64)
sudo apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-tk \
    python3-dev \
    chromium || sudo apt-get install -y chromium-browser || true \
    chromium-driver || sudo apt-get install -y chromium-chromedriver || true \
    libnss3 \
    libx11-6 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libatk-bridge2.0-0 || sudo apt-get install -y libatk-bridge2.0-0t64 || true \
    libgtk-3-0 || sudo apt-get install -y libgtk-3-0t64 || true \
    libgbm1 \
    libxrandr2 \
    libasound2 || sudo apt-get install -y libasound2t64 || true \
    libappindicator3-1 || true \
    fonts-liberation \
    xdg-utils \
    jq \
    tesseract-ocr \
    tesseract-ocr-por

# ---------------------------------------------
# 4️⃣ Instala dependências Python
# ---------------------------------------------
echo ""
echo "🐍 Instalando dependências Python..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

pip install --upgrade pip
pip install -e "$PROJECT_ROOT"

# ---------------------------------------------
# ✅ Finalização
# ---------------------------------------------
echo ""
echo "============================================="
echo "✅ Instalação local concluída com sucesso!"
echo "============================================="
