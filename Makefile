.PHONY: up dev down build test seed eval-llm logs clean migrate restart help

# ── Defaults ──────────────────────────────────────────────────────
COMPOSE       = docker compose
COMPOSE_DEV   = $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_GPU   = $(COMPOSE) -f docker-compose.yml -f docker-compose.gpu.yml

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Lifecycle ─────────────────────────────────────────────────────
up: ## Start all services (production-like)
	$(COMPOSE) up -d --build

dev: ## Start in development mode (hot reload, mailpit)
	$(COMPOSE_DEV) up --build

dev-gpu: ## Development mode with GPU for Ollama
	$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.gpu.yml up --build

down: ## Stop all services
	$(COMPOSE) down

build: ## Build all images
	$(COMPOSE) build

restart: ## Restart a service: make restart s=backend
	$(COMPOSE) restart $(s)

# ── Database ──────────────────────────────────────────────────────
migrate: ## Run database migrations
	$(COMPOSE) run --rm migrate

seed: ## Load demo data (locations, slots, users, occupancy)
	$(COMPOSE) exec backend python -m app.seed

# ── Tests ─────────────────────────────────────────────────────────
test: ## Run all tests
	$(COMPOSE) exec backend python -m pytest -v --tb=short
	$(COMPOSE) exec ai-service python -m pytest -v --tb=short

test-backend: ## Run backend tests only
	$(COMPOSE) exec backend python -m pytest -v --tb=short

test-ai: ## Run AI service tests only
	$(COMPOSE) exec ai-service python -m pytest -v --tb=short

eval-llm: ## Run LLM intent evaluation harness
	$(COMPOSE) exec ai-service python -m pytest tests/eval/ -v

# ── Observability ─────────────────────────────────────────────────
logs: ## Tail all service logs
	$(COMPOSE) logs -f

logs-backend: ## Tail backend logs
	$(COMPOSE) logs -f backend worker

logs-ai: ## Tail AI service logs
	$(COMPOSE) logs -f ai-service ollama

# ── Cleanup ───────────────────────────────────────────────────────
clean: ## Stop and remove containers, networks and volumes
	$(COMPOSE) down -v --remove-orphans

prune: ## Remove dangling images and build cache
	docker system prune -f
