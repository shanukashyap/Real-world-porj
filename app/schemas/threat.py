from pydantic import BaseModel, Field


class ThreatSearchIn(BaseModel):
    q: str = Field(..., min_length=1, max_length=256)


class ThreatIndicatorOut(BaseModel):
    ioc_type: str
    value: str
    severity: str
    description: str
    mitre_technique: str | None
    source: str
