"""Load SOC knowledge corpus into pgvector (PostgreSQL + LangChain)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import AppMeta, ThreatIndicator
from app.rag.embeddings import get_embeddings


def _sync_dsn() -> str:
    url = get_settings().database_url
    return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


def ingest_knowledge_sync(knowledge_dir: Path) -> None:
    if not knowledge_dir.is_dir():
        return

    emb = get_embeddings()

    raw_docs: list[Document] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        raw_docs.append(
            Document(
                page_content=text,
                metadata={"source": str(path.name), "type": "soc_knowledge"},
            )
        )
    if not raw_docs:
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(raw_docs)

    PGVector.from_documents(
        documents=chunks,
        embedding=emb,
        collection_name="soc_copilot",
        connection_string=_sync_dsn(),
    )


async def ingest_knowledge_corpus(knowledge_dir: Path) -> None:
    """Idempotent: skip if already ingested (same corpus version)."""

    from app.db.session import SessionLocal

    CorpusFlag = "rag_corpus_ingested"
    CorpusVer = "v1"

    async with SessionLocal() as session:
        result = await session.execute(select(AppMeta).where(AppMeta.key == CorpusFlag))
        row = result.scalar_one_or_none()
        if row and row.value == CorpusVer:
            return

    await asyncio.to_thread(ingest_knowledge_sync, knowledge_dir)

    async with SessionLocal() as session:
        session.merge(AppMeta(key=CorpusFlag, value=CorpusVer))
        await session.commit()


async def ingest_threat_json_if_exists(session: AsyncSession, path: Path) -> None:
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data.get("indicators", []):
        session.add(
            ThreatIndicator(
                ioc_type=item["ioc_type"],
                value=item["value"],
                severity=item.get("severity", "medium"),
                description=item.get("description", ""),
                mitre_technique=item.get("mitre_technique"),
                source=item.get("source", "seed"),
            )
        )
