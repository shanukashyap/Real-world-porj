# Deploy to the cloud

The API is a **Docker** image. You need **PostgreSQL with the `pgvector` extension** and a few **environment variables**.

## Option A — [Render](https://render.com) (web) + [Neon](https://neon.tech) (Postgres + pgvector)

### 1. Database (Neon)

1. Sign up at [neon.tech](https://neon.tech) and create a project.
2. Create a database; in the SQL editor run: `CREATE EXTENSION IF NOT EXISTS vector;`
3. Copy the **connection string** (URI). For this app, change the scheme to use asyncpg:
   - From: `postgresql://...` or `postgres://...`
   - To: **`postgresql+asyncpg://...`** (same user, password, host, DB, query params).

### 2. Web service (Render)

1. In [Render Dashboard](https://dashboard.render.com): **New +** → **Blueprint**.
2. Connect GitHub and select repo **`shanukashyap/Real-world-porj`** (or your fork).
3. Render loads **`render.yaml`**. Set environment variables when prompted (or after deploy):
   - **`DATABASE_URL`** — Neon string with `postgresql+asyncpg://`
   - **`SECRET_KEY`** — long random string (e.g. `openssl rand -hex 32`)
   - **`CORS_ORIGINS`** — your public API URL and dev origins, comma-separated, e.g.  
     `https://soc-ai-copilot.onrender.com,http://localhost:3000`
   - **`OPENAI_API_KEY`** — optional; RAG retrieval works without it

4. Deploy. First deploy may take several minutes (PyTorch/sentence-transformers download).  
   Open **`https://<your-service>.onrender.com/api/docs`** to try the API.

### 3. Health check

Render uses **`GET /api/v1/health`** (see `render.yaml`).

---

## Option B — AWS (summary)

- Run the same **Dockerfile** on **ECS Fargate** or **App Runner**.
- Use **RDS for PostgreSQL** with **`pgvector`** enabled ([RDS PostgreSQL extensions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)).
- Store **`SECRET_KEY`** and **`DATABASE_URL`** in **Secrets Manager**; inject as task environment variables.

---

## Required environment variables

| Variable | Required | Notes |
|----------|----------|--------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://...` — DB must have **`vector`** extension |
| `SECRET_KEY` | Yes in production | JWT signing secret |
| `CORS_ORIGINS` | Recommended | Comma-separated allowed web origins |
| `OPENAI_API_KEY` | No | Answer synthesis; otherwise retrieval-only text |
| `PORT` | Auto | Set by the platform; **Dockerfile** uses `${PORT:-8000}` |

---

## Troubleshooting

- **502 / timeout on first request**: Cold start + first-time embedding model download; wait and retry.
- **DB errors / “extension vector”**: Run `CREATE EXTENSION vector;` on the database (Neon SQL editor or RDS parameter/extension setup).
- **CORS errors from a browser**: Add your frontend origin to **`CORS_ORIGINS`**.
