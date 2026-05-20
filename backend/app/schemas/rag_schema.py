"""Pydantic schemas for RAG operations."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.constants import VALID_DOMAINS


class IngestRequest(BaseModel):
    domain: str
    force_rebuild: bool = False

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if v not in VALID_DOMAINS:
            raise ValueError(f"domain must be one of {VALID_DOMAINS}")
        return v


class IngestResponse(BaseModel):
    domain: str
    documents_processed: int
    chunks_created: int
    collection_name: str
    message: str


class RetrieveRequest(BaseModel):
    domain: str
    query: str = Field(min_length=1)
    k: Optional[int] = None

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if v not in VALID_DOMAINS:
            raise ValueError(f"domain must be one of {VALID_DOMAINS}")
        return v


class RetrieveResponse(BaseModel):
    domain: str
    query: str
    documents: list[str]
    metadatas: list[dict]
