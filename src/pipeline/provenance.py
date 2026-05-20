"""Provenance and FieldValue wrappers for extraction outputs."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.pipeline.state import BoundingBoxCoords


class ProvenanceMissingError(ValueError):
    """Raised when strict unwrapping encounters a bare scalar."""


class Provenance(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    page: int = Field(ge=0)
    bbox: BoundingBoxCoords | None = None
    source_block_id: str = ""
    extraction_path: list[str] = Field(default_factory=list)
    agent_signatures: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    vlm_model_id: str = ""
    mem0_match: str | None = None

    @field_serializer("bbox")
    def _serialize_bbox(self, bbox: BoundingBoxCoords | None, _info):
        return None if bbox is None else bbox.to_dict()

    def append_stage(self, stage: str, agent: str | None = None) -> "Provenance":
        extraction_path = [*self.extraction_path, stage]
        agent_signatures = list(self.agent_signatures)
        if agent and agent not in agent_signatures:
            agent_signatures.append(agent)
        return self.model_copy(
            update={
                "extraction_path": extraction_path,
                "agent_signatures": agent_signatures,
            }
        )

    def to_serialisable(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=False)


T = TypeVar("T")


class FieldValue(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    value: T
    provenance: Provenance

    def to_serialisable(self) -> dict[str, Any]:
        return {"value": self.value, "_provenance": self.provenance.to_serialisable()}


class PHIFieldValue(FieldValue[T], Generic[T]):
    redacted_value: str = "[REDACTED]"
    encrypted_value: bytes | None = None

    def to_serialisable(self) -> dict[str, Any]:
        out = super().to_serialisable()
        out["redacted_value"] = self.redacted_value
        if self.encrypted_value is not None:
            out["encrypted_value"] = self.encrypted_value
        return out


LEGACY_SENTINEL_PROVENANCE = Provenance(
    page=0,
    source_block_id="legacy",
    extraction_path=["legacy"],
    agent_signatures=["legacy"],
    confidence=0.0,
)


def empty_provenance(stage: str = "extraction_failed") -> Provenance:
    return Provenance(
        page=0,
        source_block_id="",
        extraction_path=[stage],
        agent_signatures=[],
        confidence=0.0,
    )


def wrap_value(value: T, provenance: Provenance | None = None) -> FieldValue[T]:
    return FieldValue(value=value, provenance=provenance or LEGACY_SENTINEL_PROVENANCE)


def is_field_value(value: Any) -> bool:
    if isinstance(value, FieldValue):
        return True
    if isinstance(value, dict):
        return "value" in value and (
            "_provenance" in value or "provenance" in value
        )
    return False


def unwrap_provenance(value: Any) -> Provenance | None:
    if isinstance(value, FieldValue):
        return value.provenance
    if isinstance(value, dict):
        payload = value.get("_provenance", value.get("provenance"))
        if isinstance(payload, Provenance):
            return payload
        if isinstance(payload, dict):
            try:
                return Provenance.model_validate(payload)
            except Exception:
                return None
    return None


def unwrap_value(value: Any, *, strict: bool = False) -> Any:
    if isinstance(value, FieldValue):
        return value.value
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    if strict and value is not None:
        raise ProvenanceMissingError("value is not wrapped with provenance")
    return value


__all__ = [
    "FieldValue",
    "LEGACY_SENTINEL_PROVENANCE",
    "PHIFieldValue",
    "Provenance",
    "ProvenanceMissingError",
    "empty_provenance",
    "is_field_value",
    "unwrap_provenance",
    "unwrap_value",
    "wrap_value",
]
