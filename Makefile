# ==========================================
# 🧠 BotUI — Root Makefile
# ==========================================

# Images
BOT_IMAGE = botui
API_IMAGE = botui-api

# Dockerfiles (AGORA dentro de BotUi_Setup)
BOT_DOCKERFILE = BotUi_Setup/Dockerfile.bot
API_DOCKERFILE = BotUi_Setup/Dockerfile.api

# Context (raiz do projeto)
CONTEXT = .

# ==========================================
# 🔨 Init All
# ==========================================
setup:
	@echo ""
	@echo "======================================"
	@echo "🏗️  Setup "
	@echo "======================================"
	make build-bot && make build-api && make run-api
	@echo "✅ All initialized!"

# ==========================================
# 🔨 BUILD BOT IMAGE
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

# ==========================================
# 🔨 BUILD API IMAGE
# ==========================================

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
# 🚀 RUN API
# ==========================================

run-api:
	@echo ""
	@echo "======================================"
	@echo "🚀 Starting BotUI API..."
	@echo "======================================"
	docker compose -f BotUi_Setup/docker-compose.yml up -d

# ==========================================
# 🧪 RUN BOT (manual debug)
# ==========================================

PATH_RUN = BotUi_Examples/run.py

run-bot:
	@echo ""
	@echo "======================================"
	@echo "🚀 Running BOT container (manual test)"
	@echo "======================================"
	docker run --rm \
		-v $(PWD)/BotUi_Examples:/app/BotUi_Examples \
		$(BOT_IMAGE) \
		python $(PATH_RUN)

# ==========================================
# 🧹 CLEAN
# ==========================================

clean-botui:
	@echo ""
	@echo "======================================"
	@echo "🧹 Cleaning ALL BotUi Docker resources..."
	@echo "======================================"

	@echo "Stopping containers..."
	-docker ps -q --filter "name=botui" | xargs -r docker stop

	@echo "Removing containers..."
	-docker ps -a -q --filter "name=botui" | xargs -r docker rm -f

	@echo "Removing images..."
	-docker images | grep botui | awk '{print $$3}' | xargs -r docker rmi -f

	@echo "Removing volumes..."
	-docker volume ls -q | grep botui | xargs -r docker volume rm

	@echo "Removing network (if exists)..."
	-docker network ls -q --filter "name=botui" | xargs -r docker network rm

	@echo "BotUi cleanup done!"

stop-botui:
	@echo ""
	@echo "======================================"
	@echo "🧹 Stop all botui containers..."
	@echo "======================================"
	docker ps -q --filter "name=botui" | xargs -r docker stop

rm-botui:
	@echo ""
	@echo "======================================"
	@echo "🧹 Prune all botui containers..."
	@echo "======================================"
	docker ps -a -q --filter "name=botui" | xargs -r docker rm -f