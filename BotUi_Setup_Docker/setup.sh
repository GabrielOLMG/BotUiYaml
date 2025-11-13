#!/bin/bash
set -e

echo ""
echo "======================================"
echo "🤖 BotUI — Verificação de Ambiente"
echo "======================================"
echo ""

# -------------------------------------
# 1️⃣ Verifica se o Docker está instalado
# -------------------------------------
if ! command -v docker &>/dev/null; then
    echo "❌ Docker não encontrado."
    echo "   ➜ Instale com: https://docs.docker.com/get-docker/"
    exit 1
else
    echo "✅ Docker encontrado: $(docker --version)"
fi

# -------------------------------------
# 2️⃣ Verifica se o Docker está rodando
# -------------------------------------
if ! docker info &>/dev/null; then
    echo "❌ O serviço Docker não está em execução!"
    echo "   ➜ Inicie com: sudo service docker start"
    exit 1
else
    echo "✅ Docker está rodando."
fi

# -------------------------------------
# 3️⃣ Verifica se o Make está instalado
# -------------------------------------
if ! command -v make &>/dev/null; then
    echo "❌ Make não encontrado."
    echo "   ➜ Instale com: sudo apt install -y make"
    exit 1
else
    echo "✅ Make encontrado: $(make --version | head -n 1)"
fi

echo ""
echo "🚀 Tudo pronto para rodar o BotUI!"
echo "--------------------------------------"
echo ""

# -------------------------------------
# 4️⃣ (Opcional) Executa o build do Docker
# -------------------------------------
read -p "⚙️  Deseja construir a imagem Docker agora? (y/n): " choice
if [[ "$choice" =~ ^[YySs]$ ]]; then
    echo ""
    echo "🛠️  Construindo imagem Docker..."
    make -C .. build SETUP_DIR=BotUi_Setup_Docker
    echo ""
    echo "✅ Imagem Docker construída com sucesso!"
    echo "   ➜ Para iniciar o container, use: make shell"
else
    echo "⏭️  Pulando build da imagem Docker."
fi

echo ""
echo "======================================"
echo "✅ Setup completo!"
echo "======================================"
