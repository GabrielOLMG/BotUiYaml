# ==========================================
# 🧠 BotUI_Setup_Docker — Build Makefile
# ==========================================

# Nome da imagem Docker
IMAGE_NAME = botui

# Caminho do Dockerfile
DOCKERFILE = Dockerfile

# ==========================================
# 🔨 Comando principal: build
# ==========================================

## 🏗️ Constrói a imagem Docker do BotUI
build:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Construindo imagem Docker: $(IMAGE_NAME)"
	@echo "======================================"
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE) ..
	@echo ""
	@echo "✅ Build concluído com sucesso!"
	@echo "💡 Agora você pode rodar: make run  (na raiz do projeto)"
	@echo "======================================"

# ==========================================
# 🧹 Limpeza opcional
# ==========================================

## 🧹 Remove imagens e containers não utilizados
clean:
	@echo ""
	@echo "======================================"
	@echo "🧹 Limpando imagens e containers antigos..."
	@echo "======================================"
	docker system prune -f
	@echo "✅ Limpeza concluída!"
