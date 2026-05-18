"""Backend protocol and shared dataclasses for VLM backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.client.lm_client import VisionRequest, VisionResponse


class VLMRole(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CRITIC = "critic"
    LITE = "lite"


@dataclass(frozen=True, slots=True)
class BackendCapabilities:
    name: str
    supports_dual_vlm: bool = False
    supports_constrained_decoding: bool = False
    supports_logprobs: bool = False
    supports_multi_image: bool = False
    supports_tensor_parallelism: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class BackendHealth:
    backend_name: str
    overall_healthy: bool
    roles: dict[VLMRole, dict[str, Any]]


@runtime_checkable
class VLMBackend(Protocol):
    name: str

    def capabilities(self) -> BackendCapabilities: ...

    def resolve(self, role: VLMRole) -> tuple[str, str]: ...

    def health(self) -> BackendHealth: ...

    def send_vision_request(
        self,
        request: "VisionRequest",
        *,
        role: VLMRole = VLMRole.PRIMARY,
        schema: dict[str, Any] | None = None,
    ) -> "VisionResponse": ...

    async def send_vision_request_async(
        self,
        request: "VisionRequest",
        *,
        role: VLMRole = VLMRole.PRIMARY,
        schema: dict[str, Any] | None = None,
    ) -> "VisionResponse": ...

    def close(self) -> None: ...
