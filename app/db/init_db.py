"""Create pgvector extension, tables, and seed reference data."""

from pathlib import Path

from sqlalchemy import func, select, text

from app.core.security import hash_password
from app.data_paths import project_root
from app.db.models import Base, ThreatIndicator, User
from app.db.session import SessionLocal, engine
from app.rag.ingest import ingest_knowledge_corpus, ingest_threat_json_if_exists


async def init_extensions_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    await _seed_if_empty()


async def _seed_if_empty() -> None:
    data_dir = project_root() / "data"

    async with SessionLocal() as session:
        user_count = await session.scalar(select(func.count()).select_from(User))
        if user_count == 0:
            session.add(
                User(
                    username="soc_analyst",
                    password_hash=hash_password("ChangeMeInProduction!"),
                )
            )
        ti_count = await session.scalar(select(func.count()).select_from(ThreatIndicator))
        if ti_count == 0:
            samples = data_dir / "threat_samples.json"
            if samples.is_file():
                await ingest_threat_json_if_exists(session, samples)

        await session.commit()

    # LangChain PGVector collection (idempotent re-ingest if empty store)
    await ingest_knowledge_corpus(Path(data_dir / "knowledge"))
