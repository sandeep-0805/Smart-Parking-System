# 🚗 SmartParking — AI-Powered Smart Parking & Mobility Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose%20v2-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-K8s%20Orchestration-326CE5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Jenkins](https://img.shields.io/badge/Jenkins-Declarative%20CI-D24939.svg?logo=jenkins&logoColor=white)](https://jenkins.io)
[![MySQL](https://img.shields.io/badge/MySQL-8.4%20LTS%20Spatial-4479A1.svg?logo=mysql&logoColor=white)](https://mysql.com)
[![Redis](https://img.shields.io/badge/Redis-7%20Alpine-DC382D.svg?logo=redis&logoColor=white)](https://redis.io)

> **Course:** SWE4008 — Application Development & Deployment Architecture  
> **Faculty Guide:** Prof. Dr. Madala Guru Brahmam Sir  
> **Slot:** L11 + L12 | **Presentation Deck:** [`SmartParking_Presentation.pptx`](SmartParking_Presentation.pptx)

---

## 🌟 Overview

**SmartParking** is a production-engineered, cloud-native mobility platform that bridges urban parking congestion through explainable machine learning, transparent pricing calibration, automated CI/CD pipelines, and Kubernetes container orchestration.

### 🛡️ Core Architectural Principles
1. **Zero-Fake Guarantee:** 49 verified, canonical Google Maps venues across 7 Indian metro hubs (Hyderabad, Bengaluru, Mumbai, NCR, Vijayawada, Pune, Chennai) with authentic basement deck slots (`B1-C01`, `B1-EV01`, `B1-M01`). Strict 5 km radius boundary enforcement.
2. **Deterministic Booking Core:** 10-minute temporary holds locking 15-minute slot intervals in MySQL with background auto-cancellation for unpaid holds.
3. **Decoupled Resiliency:** *"AI advises, backend decides."* If the AI service or local LLM is unreachable, search and booking remain 100% operational via deterministic heuristic fallbacks.
4. **Fair Pricing Calibration:** Proportional vehicle-type multipliers (0.40x for two-wheelers = ₹12/hr vs ₹30/hr for cars) and transparent occupancy surge bands (capped at 1.30x max).
5. **Enterprise DevOps:** Automated multi-stage **Jenkins CI Pipeline** paired with production-ready **Kubernetes (CD)** manifests featuring Horizontal Pod Autoscaling (HPA) and self-healing health probes.

---

## 🏛️ System Architecture

```
                                  [ Browser (React 18 SPA) ]
                                               │
                           Port 80 (HTTP)      ▼
                     ┌───────────────────────────────────┐
                     │   Reverse Proxy Gateway (Nginx)   │
                     └─────────────────┬─────────────────┘
                                       │ /api reverse-proxy
                                       ▼
                     ┌───────────────────────────────────┐
                     │   FastAPI Backend (Python 3.12)   │
                     │       Port 8000 | 3 Replicas      │
                     └───────┬─────────┬─────────┬───────┘
                             │         │         │
                Internal SQL │         │ Cache   │ REST
                             ▼         ▼         ▼
                     ┌──────────┐ ┌────────┐ ┌──────────────────────┐
                     │MySQL 8.4 │ │Redis 7 │ │AI Service (Port 8001)│
                     │ Spatial  │ │ In-Mem │ └──────────┬───────────┘
                     └──────────┘ └────────┘            │
                             ▲                          ▼
                             │                 ┌────────────────────┐
                     ┌───────┴────────┐        │Ollama (Port 11434) │
                     │APScheduler Wkr │        │ LLaMA-3.2:3b LLM   │
                     │  Hold Sweeper  │        └────────────────────┘
                     └────────────────┘
```

---

## 🚀 Quick Start (Docker Compose)

### 1. Prerequisites
- Docker Engine & Docker Compose v2+
- Git

### 2. Setup & Boot
```bash
# Clone the repository
git clone <your-repo-url>
cd SmartTraffic

# Configure environment variables
cp .env.example .env

# Start all 7 containerized services
docker compose up -d

# Verify health status
docker compose ps
```

### 3. Service Endpoints
| Service | URL | Default Port | Description |
| :--- | :--- | :--- | :--- |
| **Frontend Portal** | `http://localhost/` | `80` | React 18 SPA (Driver, Operator, Admin) |
| **Swagger API Docs** | `http://localhost:8000/docs` | `8000` | OpenAPI Interactive Documentation |
| **Backend Health** | `http://localhost:8000/api/v1/health` | `8000` | Database & Cache Health Probe |
| **AI-Service Health**| `http://localhost:8001/health` | `8001` | ML Ranker & Forecaster Health |
| **Mailpit (Dev SMTP)**| `http://localhost:8025/` | `8025` | Mock Email Testing Inbox |

---

## 🔑 Demo Role Accounts

| Role | Email | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Driver** | `driver@test.com` | `Test@1234` | Search, Proximity 0.0km ranking, 10-min hold, Razorpay pay, QR passes |
| **Operator** | `operator@test.com` | `Test@1234` | Manage parking locations, deck slots (`B1-C01`), operating hours, revenue |
| **Admin** | `admin@test.com` | `Test@1234` | Approve/suspend venues, audit users, system-wide transaction logs |

---

## ⚙️ CI/CD Pipeline (Jenkins & Automated Testing)

The repository includes a production-grade **declarative `Jenkinsfile`** executing continuous integration and automated quality gating.

### Automated Test Execution
Run the automated test suite locally or inside CI:
```cmd
# Windows Batch Runner (executes backend & AI-service tests, generates JUnit XML)
.\scripts\run_jenkins_tests.bat
```

### Test Coverage (14/14 Tests Passed)
* **Backend Suite (5 tests):**
  * `test_password_hashing`: BCrypt cryptographic security.
  * `test_jwt_access_token_creation`: PyJWT signature and TTL expiration.
  * `test_generate_blocks_15_mins`: 15-minute slot boundary alignment.
  * `test_generate_blocks_unaligned`: Arbitrary minute clamping.
  * `test_pricing_multipliers_and_clamping`: Vehicle discount (0.40x) & surge cap (1.30x).
* **AI-Service Suite (9 tests):**
  * `test_forecast_training_and_predict`: Random Forest occupancy model.
  * `test_fallback_*`: Deterministic heuristic intent parsers (search, confirm, cancel).
  * `test_rank_*`: Min-max normalization and proximity ordering.

JUnit XML test reports are automatically merged and archived into [`test-results/results.xml`](test-results/results.xml).

---

## ☸️ Kubernetes (K8s) Production Deployment

The [`k8s/`](k8s/) directory contains complete, production-ready Kubernetes manifests designed for deployment with `kustomize` or `kubectl`.

```bash
# 1. Preview compiled manifests
kubectl kustomize k8s/

# 2. Validate client dry-run
kubectl apply -k k8s/ --dry-run=client

# 3. Deploy to cluster
kubectl apply -k k8s/

# 4. Verify deployment rollout
kubectl get pods,svc,hpa -n smart-parking
```

### Kubernetes Architecture Highlights
* **Namespace Isolation:** Dedicated `smart-parking` namespace.
* **Horizontal Pod Autoscaling (HPA):** Backend scales dynamically between **2 to 5 replicas** based on 75% CPU load.
* **Self-Healing Probes:** HTTP liveness and readiness probes (`/api/v1/health` and `/health`) restart failed pods automatically.
* **Persistent Storage:** 10Gi `PersistentVolumeClaim` (`mysql-pvc`) guarantees data persistence across pod lifecycle events.
* **Unified Ingress:** Configured for `smartparking.local` with `/api` routing to backend and `/` routing to frontend SPA.

---

## 📁 Repository Structure

```
SmartTraffic/
├── Jenkinsfile                  # Jenkins declarative CI pipeline definition
├── SmartParking_Presentation.pptx # 35-slide refined defense presentation
├── docker-compose.yml           # 7-service container orchestrator
├── backend/                     # FastAPI core, raw SQL, auth, bookings, pricing
│   ├── app/                     # API routes, services, schemas, worker
│   ├── tests/                   # Pytest suite for backend services
│   └── Dockerfile               # Python 3.12 slim container
├── ai-service/                  # Machine learning microservice
│   ├── app/                     # Proximity ranker, intent parser, forecaster
│   ├── tests/                   # Pytest suite for ML services
│   └── Dockerfile               # Python 3.12 ML container
├── frontend/                    # React 18 Single Page Application
│   ├── src/                     # Pages, components, hooks, Leaflet maps
│   └── Dockerfile               # Multi-stage build + Nginx runtime
├── k8s/                         # Kubernetes production manifests
│   ├── 00-namespace.yaml        # smart-parking namespace
│   ├── 01-config-secrets.yaml   # ConfigMap & Opaque Secrets
│   ├── 02-mysql.yaml            # PVC, Deployment, Service
│   ├── 03-redis.yaml            # Deployment, Service
│   ├── 04-ai-service.yaml       # Deployment (2 replicas), Service
│   ├── 05-backend.yaml          # Deployment (3 replicas), Service, HPA
│   ├── 06-worker.yaml           # APScheduler background deployment
│   ├── 07-frontend.yaml         # Deployment (2 replicas), NodePort Service
│   ├── 08-ingress.yaml          # Nginx Ingress Controller routing
│   └── kustomization.yaml       # Kustomize manifest aggregator
├── scripts/                     # Automation & CI scripts
│   ├── run_jenkins_tests.bat    # CI test executor & JUnit XML generator
│   ├── build_presentation.py    # Python presentation builder
│   ├── export_previews.ps1      # PowerPoint COM slide exporter
│   └── render_terminals.py      # Playwright terminal screenshot renderer
├── screenshots/                 # Application & terminal verification captures
├── test-results/                # Archived JUnit XML test results
└── .env.example                 # Template environment variables
```

---

## 📊 Results & Evidence

* **49 Approved Google Maps Venues** in 7 metropolitan hubs.
* **637 Canonical Deck Slots** configured with authentic basement tier designations.
* **14 / 14 Automated Pytest Specs Passing** across Backend and AI-Service.
* **7 Containerized Services Up & Healthy** in Docker Compose.
* **9 Kubernetes Production Manifests** validated cleanly with Kustomize.
* **Proximity Mall Priority:** Searching *"Inorbit Mall"* prioritizes Inorbit Mall Cyberabad at 0.0 km (₹30/hr, slot B1-C01) ahead of distant stations.
* **Fair Two-Wheeler Rate:** Searching with `vehicle_type=MOTORCYCLE` applies 0.40x multiplier → ₹12/hr for slot B1-M01.

---

## 👥 Project Team

* **Course:** SWE4008 — Application Development & Deployment Architecture
* **Slot:** L11 + L12
* **Registration Numbers:** `23MIC7268` • `23MIC7024` • `23MIC7063` • `23MIC7255`
#   S m a r t - P a r k i n g - S y s t e m  
 