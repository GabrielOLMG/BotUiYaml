# ==========================================
# BotUI — Root Makefile (Monorepo)
# ==========================================

# Images
BOT_IMAGE = botui
API_IMAGE = botui-api

# Dockerfiles
BOT_DOCKERFILE = BotUi_Setup/Dockerfile.bot
API_DOCKERFILE = BotUi_Setup/Dockerfile.api

# Context (raiz do monorepo)
CONTEXT = .

# ==========================================
# SETUP (FULL START)
# ==========================================
setup:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Setup BotUI Monorepo"
	@echo "======================================"
	make build-bot && make build-api && make run-api
	@echo "✅ System ready!"

# ==========================================
# BUILDs
# ==========================================
build-bot:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Building BOT image: $(BOT_IMAGE)"
	@echo "======================================"
	docker build \
		-t $(BOT_IMAGE) \
		-f $(BOT_DOCKERFILE) \
		$(CONTEXT)
	@echo "✅ Bot image built!"

build-api:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Building API image: $(API_IMAGE)"
	@echo "======================================"
	docker build \
		-t $(API_IMAGE) \
		-f $(API_DOCKERFILE) \
		$(CONTEXT)
	@echo "✅ API image built!"

# ==========================================
# 🚀 RUNs
# ==========================================
run-api:
	@echo ""
	@echo "======================================"
	@echo "🚀 Starting BotUI API..."
	@echo "======================================"
	docker compose up -d
	@echo "✅ API running at http://localhost:8000"


# ==========================================
# CLEAN
# ==========================================
clean-botui:
	@echo ""
	@echo "======================================"
	@echo "🧹 Cleaning BotUI system..."
	@echo "======================================"

	-docker ps -q --filter "name=botui" | xargs -r docker stop
	-docker ps -a -q --filter "name=botui" | xargs -r docker rm -f
	-docker images | grep botui | awk '{print $$3}' | xargs -r docker rmi -f
	-docker volume ls -q | grep botui | xargs -r docker volume rm
	-docker network ls -q --filter "name=botui" | xargs -r docker network rm

	@echo "✅ Clean complete!"

stop-botui:
	@echo "🛑 Stopping all BotUI containers..."
	docker ps -q --filter "name=botui" | xargs -r docker stop
	@echo "✅ Stopped."

kill-botui:
	@echo "💀 Killing all BotUI containers..."
	docker ps -q --filter "name=botui" | xargs -r docker kill
	@echo "✅ Killed."

# ==========================================
# JOBs
# ==========================================
# make spawn-job \
#   PIPELINE_DIR=/tmp/teste \
#   BOT_RELATIVE_PATH=bot.yaml \
#   GLOBALS_RELATIVE_PATH=vars.yaml \
#   DEBUG=true

PIPELINE_DIR ?= /Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/_teste
BOT_RELATIVE_PATH ?= bot_yaml.yaml
GLOBALS_RELATIVE_PATH ?= bot_variables.yaml
DEBUG ?= false

spawn-job:
	@echo ""
	@echo "======================================"
	@echo "🚀 Spawning BotUI job..."
	@echo "======================================"
	@echo "Pipeline: $(PIPELINE_DIR)"
	@echo "Bot: $(BOT_RELATIVE_PATH)"
	@echo "Globals: $(GLOBALS_RELATIVE_PATH)"
	@echo "Debug: $(DEBUG)"
	@echo "======================================"

	curl -X POST http://localhost:8000/jobs/run \
		-H "accept: application/json" \
		-H "Content-Type: application/json" \
		-d "{\"pipeline_dir\": \"$(PIPELINE_DIR)\", \"bot_relative_path\": \"$(BOT_RELATIVE_PATH)\", \"globals_relative_path\": \"$(GLOBALS_RELATIVE_PATH)\", \"debug\": $(DEBUG)}"