"""Profile descriptor types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ProfileDescriptor:
    name: str
    display_name: str
    description: str = ""
    confidence_floor: float = 0.0
    schema_overlay_fields: tuple[str, ...] = field(default_factory=tuple)
