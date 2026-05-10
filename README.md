# SOC AI Copilot

A **real-world style** security operations assistant that combines **RAG (LangChain + PostgreSQL pgvector)**, **local NLP embeddings**, an **OWASP-minded FastAPI surface**, and **SOC-style audit logging** suitable for forwarding to a SIEM. Optional **OpenAI** synthesis turns retrieved runbooks into analyst-ready answers.

## Stack

| Area | Technologies |
|------|----------------|
| **AI / NLP** | Python, LangChain, sentence-transformers (`all-MiniLM-L6-v2`), optional OpenAI chat models |
| **Data** | PostgreSQL + **pgvector**, async SQLAlchemy |
| **API** | FastAPI, Pydantic, OAuth2 password flow + JWT |
| **Security** | Argon2 password hashing, rate limiting (SlowAPI), security headers, input validation, CORS controls |
| **Blue team / SOC** | Audit log schema for analyst actions; MITRE/OWASP knowledge corpus; IOC search demo |
| **DevOps** | Docker & Docker Compose, GitHub Actions CI |

**Cloud deploy:** use **[DEPLOY.md](DEPLOY.md)** (Render + Neon with pgvector, or AWS notes). The **Dockerfile** listens on **`PORT`** for platforms like Render.

## Quick start (Docker)

```text
cd soc-ai-copilot
docker compose up --build
```

- API: `http://localhost:8000`  
- Interactive docs: `http://localhost:8000/api/docs`  

**First startup** downloads the embedding model (sentence-transformers). Later starts are faster if you keep the container or mount a Hugging Face cache volume.

### Seeded credentials

- Username: `soc_analyst`  
- Password: `ChangeMeInProduction!`  

Register additional users via `POST /api/v1/auth/register` (password minimum length: 12).

### Optional LLM synthesis

Set `OPENAI_API_KEY` for the API service (see `docker-compose.yml`). Without it, `/api/v1/rag/ask` still returns **retrieved chunks** with a clear “LLM disabled” preamble.

## Configuration

Copy `.env.example` to `.env` for local runs outside Docker. Key variables:

- `DATABASE_URL` — async SQLAlchemy URL (`postgresql+asyncpg://…`)  
- `SECRET_KEY` — JWT signing secret (use a long random value in production)  
- `OPENAI_API_KEY` — optional  

## API outline

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/health` | Liveness |
| `POST` | `/api/v1/auth/register` | Register + JWT |
| `POST` | `/api/v1/auth/token` | OAuth2 password (form) + JWT |
| `POST` | `/api/v1/rag/ask` | RAG question (Bearer token) |
| `POST` | `/api/v1/threat-intel/search` | IOC-style search (Bearer token) |

Security events and analyst queries are stored in `audit_logs` (JSON `detail` for SIEM pipelines).

## AWS (high level)

Typical production layout:

- **Amazon RDS for PostgreSQL** with the `pgvector` extension enabled (or Aurora PostgreSQL compatible).  
- **ECS Fargate** or **EKS** running the container from this `Dockerfile`.  
- **Secrets Manager** for `SECRET_KEY` and `OPENAI_API_KEY`.  
- **Application Load Balancer** with TLS termination; restrict security groups; enable VPC flow logging for network visibility.

## Development

```text
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://soc:soc@localhost:5432/soc_copilot
uvicorn app.main:app --reload
```

```text
ruff check app tests
pytest
```

Integration test (Postgres + full app): `set INTEGRATION_TESTS=1` and `pytest -m integration`.

## License

MIT — use freely for learning and portfolio work; harden secrets and TLS before any production exposure.
