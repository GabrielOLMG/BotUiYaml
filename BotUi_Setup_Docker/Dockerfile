# ================================
# 🐳 Dockerfile — BotUI Environment (No GUI)
# ================================

FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# ================================
# 🔧 Dependências do Sistema
# ================================

RUN apt-get update -y && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    python3-tk \
    python3-dev \
    libnss3 \
    libx11-6 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libxrandr2 \
    libasound2 \
    libappindicator3-1 \
    fonts-liberation \
    xdg-utils \
    jq \
    tesseract-ocr \
    tesseract-ocr-por \
    \
    # 🔥 Xvfb + Flutter CanvasKit (NOVO)
    xvfb \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libdrm2 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    \
    && rm -rf /var/lib/apt/lists/*

# ================================
# 🧠 Playwright
# ================================

RUN pip install --no-cache-dir playwright
RUN playwright install chromium

# ============================
# 📦 Configuração da Aplicação
# ============================

WORKDIR /app
COPY ../ /app
EXPOSE 8000
RUN pip install --no-cache-dir -e .

# ============================
# ⚙️ Entrypoint e Execução
# ============================

COPY BotUi_Setup_Docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
