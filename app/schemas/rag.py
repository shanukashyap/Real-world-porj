from pydantic import BaseModel, Field


class RagQueryIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=4000)


class SourceChunk(BaseModel):
    content: str
    source: str | None = None


class RagQueryOut(BaseModel):
    answer: str
    sources: list[SourceChunk]
