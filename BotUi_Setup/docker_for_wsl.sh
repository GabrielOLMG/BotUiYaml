#!/bin/bash
set -e

# ==========================================
# 🧠 Instalação Automática do Docker no WSL
# ==========================================

echo ""
echo "============================================="
echo "🐋 Instalação Automática do Docker (para WSL)"
echo "============================================="
echo ""

# --- Função para logs coloridos ---
log() { echo -e "\033[1;36m🔹 $1\033[0m"; }
ok()  { echo -e "\033[1;32m✅ $1\033[0m"; }
warn(){ echo -e "\033[1;33m⚠️  $1\033[0m"; }
err() { echo -e "\033[1;31m❌ $1\033[0m"; }

# --- Passo 0: Remover versões antigas ---
log "[1/8] Removendo versões antigas do Docker..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc || true

# --- Passo 1: Atualizar pacotes ---
log "[2/8] Atualizando pacotes..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# --- Passo 2: Adicionar repositório oficial da Docker ---
log "[3/8] Adicionando repositório oficial da Docker..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# --- Passo 3: Instalar Docker Engine ---
log "[4/8] Instalando Docker Engine..."
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# --- Passo 4: Iniciar Docker ---
log "[5/8] Iniciando serviço Docker..."
sudo service docker start

# --- Passo 5: Verificar status ---
log "[6/8] Verificando status do Docker..."
if sudo service docker status > /dev/null 2>&1; then
    ok "Docker iniciado com sucesso!"
else
    err "Falha ao iniciar o Docker. Verifique manualmente com: sudo service docker status"
    exit 1
fi

# --- Passo 6: Corrigir permissões (sem sudo) ---
log "[7/8] Configurando permissões para o usuário atual..."
sudo groupadd docker || true
sudo usermod -aG docker $USER
sudo chmod 666 /var/run/docker.sock || warn "Socket do Docker ainda não disponível, será corrigido após reiniciar"

# --- Passo 7: Testar execução ---
log "[8/8] Testando execução com 'hello-world'..."
if docker run hello-world > /dev/null 2>&1; then
    ok "Docker testado com sucesso! Tudo funcionando ✅"
else
    warn "Docker instalado, mas o teste falhou."
    warn "Você pode tentar novamente após reiniciar o terminal."
fi

# --- Dica final ---
echo ""
ok "Instalação completa!"
echo ""
echo "💡 Dica: Reinicie o terminal ou rode:"
echo "   newgrp docker"
echo ""
echo "💡 Para iniciar automaticamente o Docker no WSL, adicione isto ao ~/.bashrc:"
echo "   if ! pgrep dockerd > /dev/null; then sudo service docker start > /dev/null 2>&1; fi"
echo ""
echo "============================================="
