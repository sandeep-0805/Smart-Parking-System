# 🚗 SmartParking — AI-Powered Smart Parking Slot Booking & Management

A full-stack web platform where **drivers** find, reserve and pay for parking, and **operators** manage inventory and watch demand. Five AI modules sit on a deterministic booking core.

> **Design rule:** AI advises, the backend decides. If every AI component is down, search and booking still work.

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — set RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, JWT_SECRET

# 2. Start everything (first run pulls ~2 GB Ollama model)
make up

# 3. Seed demo data (5 locations, 50 slots, 3 users)
make seed

# 4. Open
#   Frontend  →  http://localhost
#   API Docs  →  http://localhost:8000/docs
#   Mailpit   →  http://localhost:8025   (dev profile)
#   Adminer   →  http://localhost:8080   (tools profile)
```

### Development Mode (hot reload)

```bash
make dev
# Frontend → http://localhost:3000   (Vite HMR)
# Backend  → http://localhost:8000   (uvicorn --reload)
```

## Architecture

```
Browser (React SPA)
   │  HTTP
frontend (nginx) ─── serves SPA, proxies /api
   │
backend (FastAPI) ────→ MySQL 8.4   (source of truth)
   │   └──────────────→ Redis 7     (cache, sessions, rate limits)
   │
worker (APScheduler)    hold expiry, snapshots, auto-booking
   │
   │  REST (internal)
ai-service (FastAPI) ──→ Ollama (llama3.2:3b)
   │
backend ←──────────────→ Razorpay (test mode)
```

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.12, raw MySQL (aiomysql), Pydantic v2 |
| Frontend | React 18 + Vite, JavaScript (JSX), Tailwind CSS, TanStack Query, react-leaflet |
| Database | MySQL 8.4 LTS (InnoDB, utf8mb4, UTC) |
| Cache | Redis 7 |
| AI/ML | scikit-learn, pandas (separate FastAPI service) |
| LLM | llama3.2:3b via Ollama |
| Payments | Razorpay (test mode) |
| Maps | Leaflet + OpenStreetMap tiles |
| Auth | JWT (access + refresh tokens) |
| Packaging | Docker Compose, Git monorepo |

## AI Modules

1. **Slot Recommendation** — weighted scoring (distance, price, availability, facilities)
2. **Auto-Booking** — preference-based rules, runs through the same booking pipeline
3. **Chatbot** — Ollama intent extraction → backend tool mapping → search/book
4. **Dynamic Pricing** — occupancy band multipliers (rule-based, ML signal optional)
5. **Availability Forecasting** — Random Forest / Gradient Boosting on occupancy history

## Make Targets

| Command | Description |
|---------|-------------|
| `make up` | Start all services (production-like) |
| `make dev` | Development mode with hot reload |
| `make down` | Stop all services |
| `make seed` | Load demo locations, slots, users |
| `make test` | Run backend + AI service tests |
| `make eval-llm` | Run LLM intent evaluation harness |
| `make logs` | Tail all service logs |
| `make clean` | Stop + remove volumes |

## Demo Credentials (after `make seed`)

| Role | Email | Password |
|------|-------|----------|
| Driver | `driver@test.com` | `Test@1234` |
| Operator | `operator@test.com` | `Test@1234` |
| Admin | `admin@test.com` | `Test@1234` |

## Project Structure

```
SmartTraffic/
├── backend/          FastAPI app, services, raw SQL, worker, seed
├── ai-service/       Ranking, intent extraction, forecasting
├── frontend/         React SPA, Tailwind, Leaflet maps
├── infra/            MySQL init, Ollama init, nginx
├── docker-compose.yml / .dev.yml / .gpu.yml
├── Makefile
└── .env.example
```

## Hardware Notes

- **Ollama**: llama3.2:3b needs ~2–3 GB RAM, runs on CPU. Slower than GPU — the chat has a 20s timeout and a form fallback.
- **GPU**: use `make dev-gpu` or add `-f docker-compose.gpu.yml` if you have an NVIDIA GPU.
- **Minimum**: 8 GB free RAM recommended for the full stack.

## License

Private — not for redistribution.
