# ================================
# 🐳 Dockerfile — BotUI Environment (No GUI)
# ================================

# Imagem base com Python 3.10
FROM python:3.10-slim

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Define onde o Playwright vai instalar os browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# ================================
# 🔧 Dependências do Sistema
# ================================

# Dependências exigidas pelo Playwright + Tesseract
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
    && rm -rf /var/lib/apt/lists/*

# ================================
# 🧠 Playwright
# ================================

# Instala Playwright
RUN pip install --no-cache-dir playwright

# Instala Chromium do Playwright
RUN playwright install chromium

# ============================
# 📦 Configuração da Aplicação
# ============================

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o código principal da aplicação
COPY ../ /app

# Instala a biblioteca local em modo editável
RUN pip install --no-cache-dir -e .

# ============================
# ⚙️ Entrypoint e Execução
# ============================

# Copia o entrypoint da pasta de setup
COPY BotUi_Setup_Docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Define o entrypoint principal
ENTRYPOINT ["/entrypoint.sh"]

# Comando padrão (mantém o container interativo)
CMD ["bash"]
