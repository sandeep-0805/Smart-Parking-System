# SmartParking

AI-powered real-time parking reservation platform with proximity-first ranking, fair dynamic pricing, Jenkins CI pipeline, and Kubernetes container orchestration.

**Design rule:** AI advises, the backend decides. If every AI component goes down, search and booking still work.

## Architecture

```
Browser (React 18 SPA)
   |  HTTP
frontend (Nginx :80) --- serves SPA, proxies /api
   |
backend (FastAPI :8000) ---> MySQL 8.4 (source of truth)
   |                    ---> Redis 7   (cache, rate limits)
   |
worker (APScheduler)         hold expiry, auto-booking
   |
   |  REST (internal)
ai-service (FastAPI :8001) ---> Ollama (llama3.2:3b)
   |
backend <------------------> Razorpay (test mode)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.12, raw MySQL (aiomysql), Pydantic v2 |
| Frontend | React 18, Vite, Tailwind CSS, TanStack Query, Leaflet |
| Database | MySQL 8.4 LTS (InnoDB, spatial indexes, UTC) |
| Cache | Redis 7 Alpine |
| AI/ML | scikit-learn, pandas (separate FastAPI microservice) |
| LLM | llama3.2:3b via Ollama |
| Payments | Razorpay (test mode) |
| Maps | Leaflet + OpenStreetMap |
| Auth | JWT (access + refresh tokens, HTTP-only cookies) |
| CI | Jenkins declarative pipeline, Pytest, JUnit XML |
| CD | Kubernetes (Kustomize), HPA autoscaling, Ingress |
| Containers | Docker Compose (7 services) |

## Quick Start

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your Razorpay and JWT secrets

# Start all 7 services
docker compose up -d

# Seed demo data (49 locations, 637 slots, 3 users)
make seed

# Open
#   Frontend  ->  http://localhost
#   API Docs  ->  http://localhost:8000/docs
```

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Driver | driver@test.com | Test@1234 |
| Operator | operator@test.com | Test@1234 |
| Admin | admin@test.com | Test@1234 |

## Makefile Targets

| Command | Description |
|---------|-------------|
| `make up` | Start all services (production mode) |
| `make dev` | Development mode with hot reload |
| `make down` | Stop all services |
| `make seed` | Load demo locations, slots, users |
| `make test` | Run backend + AI service tests |
| `make logs` | Tail all service logs |
| `make clean` | Stop and remove volumes |

## CI/CD Pipeline

### Jenkins CI

The `Jenkinsfile` defines a multi-stage declarative pipeline:

1. **Checkout** - Pull source from Git
2. **Test** - Run backend and AI-service pytest suites in parallel
3. **Report** - Archive JUnit XML results (`test-results/results.xml`)
4. **Build** - Build Docker images for frontend, backend, and ai-service
5. **Validate** - Dry-run Kubernetes manifests (`kubectl apply -k k8s/ --dry-run=client`)
6. **Deploy** - Rolling update to Kubernetes cluster (main branch only)

Run tests locally:
```bash
scripts\run_jenkins_tests.bat
```

### Kubernetes Deployment

Production manifests live in `k8s/` and deploy with a single command:

```bash
kubectl apply -k k8s/
```

Key features:
- **Namespace:** `smart-parking`
- **HPA:** Backend autoscales from 2 to 5 pods at 75% CPU
- **Health probes:** Liveness and readiness on `/api/v1/health` and `/health`
- **Persistent storage:** 10Gi PVC for MySQL data
- **Ingress:** Routes `smartparking.local` with path-based routing (`/api` to backend, `/` to frontend)
- **Secrets:** DB passwords, JWT keys, and Razorpay tokens stored in Kubernetes Secrets

## AI Modules

1. **Slot Recommendation** - Weighted scoring across distance, price, availability, and facilities
2. **Auto-Booking** - Preference-based rules engine, uses the same booking pipeline
3. **Chatbot** - Ollama intent extraction with deterministic fallback parser
4. **Dynamic Pricing** - Occupancy-based surge bands (capped at 1.30x) and vehicle-type multipliers
5. **Availability Forecasting** - Random Forest model trained on occupancy history

## Project Structure

```
SmartTraffic/
|-- Jenkinsfile                    # CI pipeline definition
|-- docker-compose.yml             # 7-service orchestration
|-- Makefile                       # Dev/build shortcuts
|-- .env.example                   # Template environment config
|-- backend/                       # FastAPI backend
|   |-- app/                       # Routes, services, schemas, worker
|   |-- tests/                     # Pytest suite (5 tests)
|   +-- Dockerfile
|-- ai-service/                    # ML microservice
|   |-- app/                       # Ranker, intent parser, forecaster
|   |-- tests/                     # Pytest suite (9 tests)
|   +-- Dockerfile
|-- frontend/                      # React 18 SPA
|   |-- src/                       # Pages, components, hooks
|   +-- Dockerfile                 # Multi-stage build + Nginx
|-- k8s/                           # Kubernetes manifests
|   |-- 00-namespace.yaml
|   |-- 01-config-secrets.yaml
|   |-- 02-mysql.yaml              # PVC + Deployment + Service
|   |-- 03-redis.yaml
|   |-- 04-ai-service.yaml         # 2 replicas
|   |-- 05-backend.yaml            # 3 replicas + HPA
|   |-- 06-worker.yaml             # Background job runner
|   |-- 07-frontend.yaml           # 2 replicas + NodePort
|   |-- 08-ingress.yaml            # Nginx ingress routing
|   +-- kustomization.yaml
|-- scripts/                       # CI and automation scripts
|   |-- run_jenkins_tests.bat      # Test runner with JUnit XML output
|   +-- build_presentation.py
|-- screenshots/                   # App and terminal captures
|-- test-results/                  # Archived JUnit XML reports
+-- infra/                         # MySQL init, Ollama init, Nginx config
```

## Hardware Notes

- **Ollama:** llama3.2:3b needs ~2-3 GB RAM, runs on CPU. The chat has a 20s timeout with a form fallback.
- **GPU:** Use `make dev-gpu` or add `-f docker-compose.gpu.yml` for NVIDIA GPU acceleration.
- **Minimum:** 8 GB free RAM recommended for the full stack.
