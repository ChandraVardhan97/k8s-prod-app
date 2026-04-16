# 🚀 Production Kubernetes Deployment Pipeline

> A complete, production-grade deployment pipeline running locally — from code to cluster with GitOps, auto-scaling, and full observability.

[![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.35-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![ArgoCD](https://img.shields.io/badge/ArgoCD-GitOps-EF7B4D?logo=argo&logoColor=white)](https://argoproj.github.io/cd/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Docker](https://img.shields.io/badge/Docker-Hub-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/chandubodduluri/bookshelf-api)
[![Helm](https://img.shields.io/badge/Helm-Charts-0F1689?logo=helm&logoColor=white)](https://helm.sh/)

---

## Architecture

```
Developer → Docker Hub → Kind Cluster (4 nodes)
                              ├── ArgoCD     (watches this repo → auto-deploys)
                              ├── App Pods   (2 replicas, HPA auto-scaling)
                              ├── Prometheus (scrapes /metrics via ServiceMonitor)
                              └── Grafana    (9-panel dashboard)
```

### The Pipeline

| Path | Flow |
|------|------|
| **Container Image** | Code → Docker Build → Docker Hub |
| **GitOps (Config)** | Helm Chart → GitHub → ArgoCD → K8s Manifests → Running Pods |
| **Observability** | App `/metrics` → Prometheus → Grafana Dashboards |

---

## 📦 The Application — Bookshelf API

A production-relevant **FastAPI** REST service with health checks, structured logging, Prometheus metrics, and graceful shutdown.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/books` | `GET` | List all books (paginated) |
| `/books` | `POST` | Create a book |
| `/books/{id}` | `GET` | Get a book by ID |
| `/books/{id}` | `PUT` | Update a book |
| `/books/{id}` | `DELETE` | Delete a book |
| `/healthz` | `GET` | Liveness probe |
| `/readyz` | `GET` | Readiness probe (checks DB) |
| `/metrics` | `GET` | Prometheus metrics |
| `/docs` | `GET` | Swagger UI |

### Production Patterns Implemented

- ✅ **Health checks** — Kubernetes liveness & readiness probes
- ✅ **Prometheus metrics** — Request count, duration histograms, business metrics
- ✅ **Structured JSON logging** — Machine-parseable for log aggregation
- ✅ **Graceful shutdown** — In-flight requests complete before pod termination
- ✅ **Config via environment variables** — Same image across all environments
- ✅ **Non-root Docker user** — Minimal attack surface
- ✅ **Multi-stage Docker build** — ~150MB production image

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Application** | Python 3.12, FastAPI, SQLAlchemy, SQLite, Pydantic |
| **Containerization** | Docker (multi-stage, non-root) |
| **Orchestration** | Kubernetes (Kind — 1 control plane + 3 workers) |
| **Package Management** | Helm (7 templated manifests) |
| **GitOps** | ArgoCD (auto-sync, prune, self-heal) |
| **Observability** | Prometheus + Grafana (9-panel custom dashboard) |
| **Auto-scaling** | HPA (2–6 replicas, 70% CPU target) |

---

## ⚡ Quick Start

### Prerequisites

```bash
# Windows (Chocolatey)
choco install kubernetes-cli kubernetes-helm kind docker-desktop -y
```

### 1. Create the Cluster

```bash
kind create cluster --config kind-config.yaml
```

### 2. Deploy via ArgoCD (GitOps)

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Deploy the app (ArgoCD watches this repo)
kubectl apply -f argocd-app.yaml
```

### 3. Or Deploy Directly with Helm

```bash
helm install bookshelf-api ./helm/bookshelf-api \
  --namespace bookshelf --create-namespace
```

### 4. Run Locally with Docker

```bash
docker pull chandubodduluri/bookshelf-api:1.0.0
docker run -p 8000:8000 chandubodduluri/bookshelf-api:1.0.0
# Open http://localhost:8000/docs
```

---

## 🔗 Access the Stack

| Service | Command | URL |
|---------|---------|-----|
| **Bookshelf API** | `kubectl port-forward svc/bookshelf-api-bookshelf-api -n bookshelf 8000:80` | http://localhost:8000/docs |
| **ArgoCD** | `kubectl port-forward svc/argocd-server -n argocd 8443:443` | https://localhost:8443 |
| **Grafana** | `kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80` | http://localhost:3000 |
| **Prometheus** | `kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090` | http://localhost:9090 |

> **Credentials:** ArgoCD → `admin` / run `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d` · Grafana → `admin` / `admin123`

---

## 📂 Project Structure

```
.
├── app/                        # Application source code
│   ├── main.py                 #   FastAPI app, health checks, metrics middleware
│   ├── models.py               #   SQLAlchemy models + Pydantic schemas
│   ├── database.py             #   Database engine configuration
│   ├── routes.py               #   CRUD endpoints
│   └── metrics.py              #   Prometheus instrumentation
├── helm/bookshelf-api/         # Helm chart
│   ├── Chart.yaml              #   Chart metadata
│   ├── values.yaml             #   Configuration values (single source of truth)
│   └── templates/              #   Kubernetes manifest templates
│       ├── deployment.yaml     #     Pod specification
│       ├── service.yaml        #     Network exposure
│       ├── ingress.yaml        #     External routing (NGINX)
│       ├── hpa.yaml            #     Auto-scaling rules
│       ├── serviceaccount.yaml #     Security identity
│       ├── servicemonitor.yaml #     Prometheus scraping config
│       └── _helpers.tpl        #     Reusable template functions
├── Dockerfile                  # Multi-stage, non-root build
├── argocd-app.yaml             # ArgoCD Application manifest
├── grafana-dashboard.yaml      # 9-panel Grafana dashboard (ConfigMap)
├── requirements.txt            # Python dependencies
```

---

## 🔄 GitOps Workflow

The deployment is fully automated via ArgoCD:

```
1. Edit values.yaml (e.g., change replicaCount: 2 → 3)
2. git commit && git push
3. ArgoCD detects the change (~3 min)
4. ArgoCD re-renders Helm templates
5. ArgoCD applies the diff to the cluster
6. New pod starts, old traffic drains gracefully
```

**Self-healing:** If someone manually changes the cluster (`kubectl scale ...`), ArgoCD automatically reverts it to match Git.

---

## 📊 Grafana Dashboard

The custom dashboard includes 9 panels covering the key monitoring signals:

| Panel | Type | Metric |
|-------|------|--------|
| Request Rate | Time Series | `rate(http_requests_total[5m])` |
| Error Rate (5xx) | Time Series | `rate(http_requests_total{status=~"5.."}[5m])` |
| Latency (P50/P95/P99) | Time Series | `histogram_quantile(0.95, ...)` |
| Active Pods | Stat | `kube_deployment_status_replicas_available` |
| Books Created | Stat | `books_created_total` |
| CPU Usage | Time Series | `container_cpu_usage_seconds_total` |
| Memory Usage | Time Series | `container_memory_working_set_bytes` |
| Status Codes | Pie Chart | `http_requests_total by (status)` |
| Requests by Endpoint | Table | `http_requests_total by (endpoint, method)` |

---

## 🛑 Cluster Management

```bash
# Stop the cluster (frees memory)
docker stop learning-cluster-control-plane learning-cluster-worker learning-cluster-worker2 learning-cluster-worker3

# Restart the cluster (all pods auto-recover from etcd state)
docker start learning-cluster-control-plane learning-cluster-worker learning-cluster-worker2 learning-cluster-worker3
```

---

## License

This project is for learning purposes. Feel free to use it as a template for your own production deployment pipelines.
