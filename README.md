# Bookshelf API — Kubernetes Production Deployment Learning Project

A production-relevant REST API deployed on a local Kind cluster with full GitOps, observability, and auto-scaling.

## Architecture

```
Developer → Docker Hub → Kind Cluster
                            ├── ArgoCD (watches this repo → auto-deploys)
                            ├── Prometheus (scrapes /metrics)
                            └── Grafana (dashboards)
```

## Application

**Bookshelf API** — A FastAPI REST service for managing a book collection.

| Endpoint | Description |
|----------|-------------|
| `GET /books` | List all books (paginated) |
| `POST /books` | Create a book |
| `GET /books/{id}` | Get a book |
| `PUT /books/{id}` | Update a book |
| `DELETE /books/{id}` | Delete a book |
| `GET /healthz` | Liveness probe |
| `GET /readyz` | Readiness probe |
| `GET /metrics` | Prometheus metrics |
| `GET /docs` | Swagger UI |

## Quick Start

### Docker
```bash
docker pull chandubodduluri/bookshelf-api:1.0.0
docker run -p 8000:8000 chandubodduluri/bookshelf-api:1.0.0
```

### Helm (on Kind cluster)
```bash
helm install bookshelf-api ./helm/bookshelf-api --namespace bookshelf --create-namespace
```

### ArgoCD (auto-deploy from this repo)
```bash
kubectl apply -f argocd-app.yaml
```

## Docker Image

`chandubodduluri/bookshelf-api:1.0.0` on [Docker Hub](https://hub.docker.com/r/chandubodduluri/bookshelf-api)

## Tech Stack

- **App**: Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Containerization**: Docker (multi-stage, non-root)
- **Orchestration**: Kubernetes (Kind), Helm
- **GitOps**: ArgoCD
- **Observability**: Prometheus + Grafana
