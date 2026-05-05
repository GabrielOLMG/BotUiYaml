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


setup-app:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Setup App UI"
	@echo "======================================"
	make build-app && make run-app
	@echo "✅ APP ready!"

setup-api:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Setup API"
	@echo "======================================"
	make build-api && make run-api
	@echo "✅ APP ready!"
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
	@echo "🏗️  Building API: "
	@echo "======================================"
	docker compose build --no-cache api
	@echo "✅ API image built!"

build-app:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Building APP: "
	@echo "======================================"
	docker compose build --no-cache dashboard
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
	docker run -it --rm -v $(MOUNT_DEBUG):/app/data --name debug $(BOT_IMAGE) bash -c "cd /app/data/template_matching && exec bash"

# ==========================================
# CLEAN
# ==========================================
clean-botui:
	@echo ""
	@echo "======================================"
	@echo "🧹 Cleaning BotUI system..."
	@echo "======================================"

	# Stop containers
	-docker ps --format '{{.ID}} {{.Names}}' | grep botui | awk '{print $$1}' | xargs -r docker stop

	# Remove containers
	-docker ps -a --format '{{.ID}} {{.Names}}' | grep botui | awk '{print $$1}' | xargs -r docker rm -f

	# Remove images
	-docker images --format '{{.Repository}} {{.ID}}' | grep botui | awk '{print $$2}' | xargs -r docker rmi -f

	# Remove volumes
	-docker volume ls --format '{{.Name}}' | grep botui | xargs -r docker volume rm

	# Remove networks
	-docker network ls --format '{{.Name}}' | grep botui | xargs -r docker network rm

	@echo "✅ Clean complete!"
	
stop-botui:
	@echo "🛑 Stopping all BotUI containers..."
	-docker ps -q | grep botui | xargs -r docker stop
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