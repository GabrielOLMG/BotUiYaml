# ==========================================
# BotUI — Root Makefile (Monorepo)
# ==========================================

# Images
BOT_IMAGE = botui
API_IMAGE = botui-api
APP_IMAGE = botui-app


# Dockerfiles
BOT_DOCKERFILE = BotUi_Setup/Dockerfile.bot
API_DOCKERFILE = BotUi_Setup/Dockerfile.api
APP_DOCKERFILE = BotUi_Setup/Dockerfile.app


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
	make build-bot && make build-api && make build-app && make run-api && make run-app
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

build-app:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Building APP image: $(APP_IMAGE)"
	@echo "======================================"
	docker build \
		-t $(APP_IMAGE) \
		-f $(APP_DOCKERFILE) \
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
	docker compose up api -d
	@echo "✅ API running at http://localhost:8000"

run-app:
	@echo ""
	@echo "======================================"
	@echo "🚀 Starting BotUI FRONT-END..."
	@echo "======================================"
	docker compose up dashboard -d
	@echo "✅ APP running at http://localhost:8501"


# ==========================================
# DEBUG
# ==========================================
MOUNT_DEBUG ?= "/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/_debug"

debug-botui-container:
	@echo ""
	@echo "======================================"
	@echo "🚀 Creating debug container for botui"
	@echo "======================================"
	docker run -it --rm -v $(MOUNT_DEBUG):/app/data --name debug $(BOT_IMAGE) bash -c "cd /app/data && exec bash"

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