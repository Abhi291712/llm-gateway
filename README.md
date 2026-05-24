# LLM Gateway

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-1.40+-green.svg)](https://litellm.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

A production-inspired API gateway for multi-provider LLM applications. Handles routing, fallbacks, caching, guardrails, cost tracking, and observability in one unified layer — so your application never goes down because one provider does.

> On November 8, 2023, OpenAI experienced a 4-hour outage. Applications built on a single provider went completely dark. This gateway prevents that.

---

## Problem

| Pain Point | Without Gateway | With Gateway |
|---|---|---|
| Multiple SDKs | Separate integration per provider | One unified API |
| Provider outage | Application goes down | Automatic fallback to backup model |
| Cost visibility | Manual logging per provider | Built-in per-call token and dollar tracking |
| Repeated queries | Full LLM cost every time | Cache hit = zero cost |
| PII in prompts | Reaches the LLM | Redacted before API call |
| Model switching | Rewrite application code | Configuration change only |
| No retries | Single failure = user error | Exponential backoff with jitter |
| Runaway costs | No spending controls | Per-user and per-key budget limits |

---

## Architecture

```
User Request
      |
      v
FastAPI Server (REST + Streaming)
      |
      v
JWT Authentication
      |
      v
Rate Limiter
Per-user and per-IP request throttling
      |
      v
Input Guardrails
PII Redaction + Prompt Injection Detection
      |
      v
Smart Router
Task classifier assigns optimal model chain
      |
      v
Cache Layer
Exact Match → Semantic Match (FAISS) → Miss
      |
      v (cache miss)
Load Balancer
API key rotation across provider keys
      |
      v
Primary Model Call (LiteLLM)
      |
      v (on failure)
Exponential Backoff + Retry with Jitter
      |
      v (retries exhausted)
Fallback Chain
Model 2 → Model 3 → Final fallback
      |
      v
Circuit Breaker
Repeated failures open the circuit — provider skipped
      |
      v
Cost Tracking + Budget Control
Token count, dollar cost, per-user spend limit
      |
      v
Observability
LangFuse tracing + Prometheus metrics
      |
      v
Response to User
```

---

## Features

| Feature | Description |
|---|---|
| Unified API | One function call works across OpenAI, Anthropic, Groq, Gemini |
| Automatic Fallbacks | Primary fails — auto-switches to backup model |
| Smart Routing | Task classifier routes each query to the optimal model |
| Exponential Backoff | Retries with jitter before triggering fallback |
| Circuit Breaker | Opens circuit on repeated failures — prevents cascade |
| Multi-layer Cache | Exact match → semantic similarity (FAISS) → full call |
| PII Redaction | Masks emails, phone numbers, SSN before reaching LLM |
| Prompt Injection Detection | Blocks jailbreak and instruction override attempts |
| Cost Tracking | Per-call token count and dollar cost across providers |
| Budget Controls | Per-user and per-key spending limits |
| Rate Limiting | Per-user and per-IP request throttling |
| JWT Authentication | Secure API access with token-based auth |
| Streaming | Server-sent events (SSE) for token-by-token response |
| Observability | Full request tracing via LangFuse + Prometheus metrics |
| Load Balancing | API key rotation to distribute provider load |

---

## Routing Logic

Routing decisions are based on measurable signals — not keyword matching.

| Signal | Action |
|---|---|
| Token length > 8000 | Route to large context model |
| Task type = code | Route to GPT-4o |
| Task type = summary | Route to GPT-4o-mini or Groq |
| Task type = general | Route to Groq Llama 3.3 (lowest cost) |
| Latency threshold exceeded | Switch to faster model |
| Cost limit reached | Route to cheaper model |
| Primary model fails | Trigger exponential backoff → fallback chain |

---

## Cache Layers

```
Query
  |
  v
Exact Match (Redis)
Same string as previous query → return instantly, zero cost
  |
  v (no match)
Semantic Match (FAISS)
Embedding similarity > 0.95 → return cached response
  |
  v (no match)
Full LLM Call
Response stored in both cache layers
```

---

## Reliability Patterns

| Pattern | Implementation |
|---|---|
| Retry | Up to 3 attempts with exponential backoff and jitter |
| Circuit Breaker | Opens after 5 consecutive failures, resets after 60 seconds |
| Fallback Chain | Primary → Secondary → Tertiary model |
| Timeout | Per-request timeout with configurable threshold |
| Rate Limiting | Token bucket algorithm per user and per IP |

---

## Stack

| Layer | Technology |
|---|---|
| API Server | FastAPI + Uvicorn |
| LLM Abstraction | LiteLLM |
| Authentication | JWT (python-jose) |
| Rate Limiting | SlowAPI |
| Semantic Cache | FAISS + HuggingFace Embeddings |
| Exact Cache | Redis |
| PII Redaction | Microsoft Presidio |
| Observability | LangFuse + Prometheus |
| Retry Logic | Tenacity |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
llm-gateway/
├── src/
│   ├── main.py                      # FastAPI server entry point
│   ├── config.py                    # Central configuration
│   ├── basic_completion.py          # Unified LLM call across providers
│   ├── fallbacks.py                 # Automatic fallback chain
│   ├── smart_router.py              # Task classification and model routing
│   ├── load_balancer.py             # API key rotation
│   ├── cost_tracking.py             # Per-call cost and budget control
│   ├── circuit_breaker.py           # Circuit breaker pattern
│   ├── streaming.py                 # SSE token streaming
│   ├── auth/
│   │   ├── jwt_handler.py           # JWT token creation and validation
│   │   └── routes.py                # Auth endpoints
│   ├── caching/
│   │   ├── exact_cache.py           # Redis string match cache
│   │   ├── semantic_cache.py        # FAISS embedding similarity cache
│   │   └── prompt_cache.py          # Prefix caching for large prompts
│   ├── guardrails/
│   │   ├── pii_redaction.py         # Presidio-based PII masking
│   │   └── prompt_injection.py      # Injection detection and blocking
│   └── observability/
│       ├── langfuse_integration.py  # Request tracing
│       └── prometheus_metrics.py    # Latency, cost, cache hit metrics
├── tests/
│   └── test_gateway.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## API Reference

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | /v1/chat/completions | Standard chat completion | Bearer |
| POST | /v1/chat/stream | Streaming token response (SSE) | Bearer |
| GET | /v1/models | List available models | Bearer |
| GET | /v1/cost | Cost report for current user | Bearer |
| GET | /health | Gateway health check | Public |
| POST | /auth/login | Authenticate and receive JWT | Public |

---

## Quick Start

```bash
git clone https://github.com/Abhi291712/llm-gateway.git
cd llm-gateway
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env
uvicorn src.main:app --reload
```

API documentation available at `http://localhost:8000/docs`

---

## Configuration

```bash
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=

JWT_SECRET_KEY=
JWT_EXPIRY_MINUTES=30

REDIS_URL=redis://localhost:6379
SEMANTIC_THRESHOLD=0.95

MAX_COST_PER_USER=10.00
MAX_COST_PER_KEY=100.00

LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
PROMETHEUS_PORT=9090
```

---

## Observability

| Metric | Source |
|---|---|
| Request latency (p50, p95, p99) | Prometheus |
| Cache hit rate | Prometheus |
| Fallback frequency | Prometheus |
| Cost per call | LangFuse + cost_tracking.py |
| Token usage per user | LangFuse |
| Circuit breaker state | Prometheus |
| PII redaction events | Structured logs |

---

## Limitations

| Area | Current Limitation |
|---|---|
| PII Redaction | Regex and Presidio-based — does not catch all edge cases |
| Prompt Injection | Classifier-based detection — sophisticated attacks may bypass |
| Semantic Cache | Requires embedding call — adds ~50ms latency on cache miss |
| Circuit Breaker | Per-instance state — not shared across horizontally scaled pods |
| Multi-modal | Text only — images and audio not supported |

---

## Future Work

- Adaptive routing using historical latency and cost signals
- Kubernetes deployment with horizontal scaling
- Distributed circuit breaker state via Redis
- Multi-modal support for images and audio
- Fine-tuned model proxy support
- OpenTelemetry integration

---

## Docker

```bash
docker-compose up --build
```

| Service | Port |
|---|---|
| Gateway API | 8000 |
| Redis | 6379 |
| Prometheus | 9090 |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

Abhishek Kumar — [LinkedIn](https://linkedin.com/in/abhishek-k-16239ba7/)
