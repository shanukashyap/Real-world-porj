"""LangChain RAG chain: retrieve from pgvector + optional LLM synthesis (GPT-4 class models)."""

from __future__ import annotations

import asyncio

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import PGVector
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.rag.embeddings import get_embeddings


def _sync_dsn() -> str:
    return get_settings().database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )


def _build_vectorstore() -> PGVector:
    return PGVector(
        connection_string=_sync_dsn(),
        embedding_function=get_embeddings(),
        collection_name="soc_copilot",
    )


async def run_rag(question: str, k: int = 4) -> tuple[str, list[dict[str, str | None]]]:
    def _sync() -> tuple[str, list[dict[str, str | None]]]:
        store = _build_vectorstore()
        docs = store.similarity_search(question, k=k)
        sources: list[dict[str, str | None]] = [
            {
                "content": d.page_content[:800],
                "source": d.metadata.get("source") if d.metadata else None,
            }
            for d in docs
        ]
        context = "\n\n---\n\n".join(d.page_content for d in docs)
        settings = get_settings()
        if settings.openai_api_key:
            llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                temperature=0,
            )
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an expert SOC analyst assistant. Answer using ONLY the context "
                        "when possible. If context is insufficient, say so and suggest general "
                        "security practices (OWASP, MITRE, logging). Be concise and actionable.",
                    ),
                    ("human", "Context:\n{context}\n\nQuestion: {question}"),
                ]
            )
            chain = prompt | llm | StrOutputParser()
            answer = chain.invoke({"context": context, "question": question})
        else:
            answer = (
                "[LLM disabled: set OPENAI_API_KEY for synthesis] "
                "Retrieved context snippets:\n\n" + context[:6000]
            )
        return answer, sources

    return await asyncio.to_thread(_sync)
