"""RAG analyst assistant — LangChain + pgvector (audit events for SIEM-style pipelines)."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import client_ip, get_current_user, get_db
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import AuditLog, User
from app.rag.chain import run_rag
from app.schemas.rag import RagQueryIn, RagQueryOut, SourceChunk

router = APIRouter(prefix="/rag", tags=["rag"])
settings = get_settings()


@router.post("/ask", response_model=RagQueryOut)
@limiter.limit(settings.rate_limit_rag)
async def ask(
    request: Request,
    body: RagQueryIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RagQueryOut:
    answer, source_dicts = await run_rag(body.question)
    sources = [
        SourceChunk(content=s["content"] or "", source=s.get("source")) for s in source_dicts
    ]
    db.add(
        AuditLog(
            user_id=user.id,
            event_type="rag_query",
            detail={
                "question_len": len(body.question),
                "sources_count": len(sources),
                "has_llm": bool(settings.openai_api_key),
            },
            source_ip=client_ip(request),
        )
    )
    return RagQueryOut(answer=answer, sources=sources)
