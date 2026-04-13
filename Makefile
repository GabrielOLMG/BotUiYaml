# ==========================================
# 🧠 Makefile — BotUI Docker Utilities
# ==========================================

# Nome da imagem Docker
IMAGE_NAME = botui

# Caminho padrão do script Python
SCRIPT ?= BotUi_Examples/run.py

# Caminho da pasta de setup (onde está o Dockerfile e entrypoint)
SETUP_DIR = BotUi_Setup_Docker

# ==========================================
# 🔨 Comandos principais
# ==========================================

## 🏗️ Build da imagem Docker (chama o make interno)
build:
	@echo "====================================="
	@echo "🏗️  Construindo imagem Docker: $(IMAGE_NAME)"
	@echo "📂 Diretório de setup: $(SETUP_DIR)"
	@echo "====================================="
	@$(MAKE) -C $(SETUP_DIR) build
	@echo ""
	@echo "✅ Build concluído com sucesso via $(SETUP_DIR)/Makefile!"
	@echo ""

## 🐚 Abre um shell interativo dentro do container
shell:
	@echo "====================================="
	@echo "🐚 Abrindo shell dentro do container..."
	@echo "====================================="
	docker run -it --rm \
		-p 8000:8000 \
		--entrypoint bash \
		-v $(PWD):/app \
		--workdir /app \
		$(IMAGE_NAME)


## 🚀 Executa a biblioteca (padrão: run.py)
run:
	@echo "====================================="
	@echo "🚀 Executando script padrão: $(SCRIPT)"
	@echo "====================================="
	docker run --rm -p 8000:8000 \
		-v $(PWD):/app \
		--workdir /app \
		$(IMAGE_NAME) \
		python3 $(SCRIPT)

run-api:
	docker run --rm -p 8000:8000 \
			-v $(PWD):/app \
			--workdir /app \
			$(IMAGE_NAME) \
			uvicorn BotUi.api.init_api:app --host 0.0.0.0 --port 8000


# ==========================================
# 🔍 Testes e Diagnóstico
# ==========================================

## 🧪 Testa o ambiente interno do container
test-env:
	@echo ""
	@echo "\033[1;36m=============================================\033[0m"
	@echo "🧪 \033[1;36mTestando ambiente da imagem Docker\033[0m"
	@echo "\033[1;36m=============================================\033[0m"
	@echo ""
	@docker run --rm $(IMAGE_NAME) bash -c '\
		GREEN="\033[1;32m"; RED="\033[1;31m"; CYAN="\033[1;36m"; NC="\033[0m"; \
		echo -e "$$CYAN🔍 Verificando binários principais...$$NC"; \
		echo ""; \
		if command -v python3 >/dev/null 2>&1; then \
			echo -e "$$GREEN✅ Python encontrado: $$(python3 --version)$$NC"; \
		else \
			echo -e "$$RED❌ Python não encontrado$$NC"; \
		fi; \
		if command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; then \
			echo -e "$$GREEN✅ Chromium encontrado: $$(chromium --version 2>/dev/null || chromium-browser --version 2>/dev/null)$$NC"; \
		else \
			echo -e "$$RED❌ Chromium não encontrado$$NC"; \
		fi; \
		if command -v chromedriver >/dev/null 2>&1; then \
			echo -e "$$GREEN✅ ChromeDriver encontrado: $$(chromedriver --version)$$NC"; \
		else \
			echo -e "$$RED❌ ChromeDriver não encontrado$$NC"; \
		fi; \
		if command -v tesseract >/dev/null 2>&1; then \
			echo -e "$$GREEN✅ Tesseract encontrado: $$(tesseract --version | head -n 1)$$NC"; \
		else \
			echo -e "$$RED❌ Tesseract não encontrado$$NC"; \
		fi; \
		echo ""; \
		echo -e "$$CYAN---------------------------------------------$$NC"; \
		echo -e "$$GREEN✅ Teste completo!$$NC"; \
		echo -e "$$CYAN---------------------------------------------$$NC"; \
	'


# ==========================================
# 🧹 Limpeza
# ==========================================

## 🧹 Remove containers, volumes e imagens não utilizadas
clean:
	@echo "====================================="
	@echo "🧹 Limpando ambiente Docker..."
	@echo "====================================="
	docker system prune -f
	@echo "✅ Limpeza concluída!"
