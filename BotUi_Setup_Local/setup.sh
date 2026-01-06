#!/bin/bash
set -e

ENV_NAME="botui"
PYTHON_VERSION="3.10"

echo ""
echo "============================================="
echo "🤖 BotUI — Configuração Local (Conda + Playwright)"
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
# 2️⃣ Verifica Conda
# ---------------------------------------------
if ! command -v conda >/dev/null 2>&1; then
    echo "❌ Conda não encontrado."
    echo "➡️  Instale Miniconda ou Anaconda antes de continuar."
    echo "   https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda encontrado"

# ---------------------------------------------
# 3️⃣ Cria ambiente Conda (se não existir)
# ---------------------------------------------
if conda env list | grep -q "^$ENV_NAME "; then
    echo "✅ Ambiente Conda '$ENV_NAME' já existe"
else
    echo "🐍 Criando ambiente Conda '$ENV_NAME' (Python $PYTHON_VERSION)..."
    conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
fi

# ---------------------------------------------
# 4️⃣ Ativa ambiente
# ---------------------------------------------
echo "🔑 Ativando ambiente Conda '$ENV_NAME'"

# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "➡️  Python ativo: $(python --version)"

# ---------------------------------------------
# 5️⃣ Dependências do sistema (IGUAL ao Docker)
# ---------------------------------------------
echo ""
echo "🔧 Instalando dependências do sistema..."

sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
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
# 6️⃣ Python deps + projeto
# ---------------------------------------------
echo ""
echo "🐍 Instalando dependências Python..."

python -m pip install --upgrade pip

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

pip install -e "$PROJECT_ROOT"
pip install playwright

# ---------------------------------------------
# 7️⃣ Chromium do Playwright
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
echo "➡️  Para usar:"
echo "   conda activate botui"
echo "============================================="
