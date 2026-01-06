#!/bin/bash
set -e

echo ""
echo "============================================="
echo "🤖 BotUI — Configuração Local (Playwright)"
echo "============================================="
echo ""

# ---------------------------------------------
# 1️⃣ Detecta ambiente
# ---------------------------------------------
if grep -qi microsoft /proc/version; then
    echo "💻 Ambiente detectado: WSL"
else
    echo "💻 Ambiente detectado: Linux nativo"
fi

# ---------------------------------------------
# 2️⃣ Atualiza lista de pacotes
# ---------------------------------------------
echo ""
echo "📦 Atualizando lista de pacotes..."
sudo apt-get update -y

# ---------------------------------------------
# 3️⃣ Dependências do sistema (IGUAL ao Docker)
# ---------------------------------------------
echo ""
echo "🔧 Instalando dependências do sistema..."

sudo apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-tk \
    python3-dev \
    wget \
    gnupg \
    ca-certificates \
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
    tesseract-ocr-por \
    xvfb \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libdrm2 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2

# ---------------------------------------------
# 4️⃣ Python + Playwright
# ---------------------------------------------
echo ""
echo "🐍 Instalando dependências Python..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

python3 -m pip install --upgrade pip
pip install -e "$PROJECT_ROOT"
pip install playwright

# ---------------------------------------------
# 5️⃣ Instala Chromium do Playwright
# ---------------------------------------------
echo ""
echo "🌐 Instalando Chromium (Playwright)..."
playwright install chromium

# ---------------------------------------------
# ✅ Finalização
# ---------------------------------------------
echo ""
echo "============================================="
echo "✅ Setup local concluído com sucesso!"
echo "============================================="
