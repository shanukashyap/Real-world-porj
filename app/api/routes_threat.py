"""Threat intelligence-style IOC search (network security / TI workflow)."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import client_ip, get_current_user, get_db
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import AuditLog, ThreatIndicator, User
from app.schemas.threat import ThreatIndicatorOut, ThreatSearchIn

router = APIRouter(prefix="/threat-intel", tags=["threat-intel"])
settings = get_settings()


@router.post("/search", response_model=list[ThreatIndicatorOut])
@limiter.limit(settings.rate_limit_default)
async def search_iocs(
    request: Request,
    body: ThreatSearchIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ThreatIndicatorOut]:
    term = f"%{body.q.strip()}%"
    result = await db.execute(
        select(ThreatIndicator)
        .where(
            or_(
                ThreatIndicator.value.ilike(term),
                ThreatIndicator.description.ilike(term),
                ThreatIndicator.mitre_technique.ilike(term),
            )
        )
        .limit(50)
    )
    rows = result.scalars().all()

    db.add(
        AuditLog(
            user_id=user.id,
            event_type="threat_intel_search",
            detail={"query": body.q, "result_count": len(rows)},
            source_ip=client_ip(request),
        )
    )

    return [
        ThreatIndicatorOut(
            ioc_type=r.ioc_type,
            value=r.value,
            severity=r.severity,
            description=r.description,
            mitre_technique=r.mitre_technique,
            source=r.source,
        )
        for r in rows
    ]
