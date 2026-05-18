"""LM Studio backend adapter."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from src.client.backends.protocol import (
    BackendCapabilities,
    BackendHealth,
    VLMBackend,
    VLMRole,
)
from src.client.lm_client import LMStudioClient
from src.config import get_logger

if TYPE_CHECKING:
    from src.client.lm_client import VisionRequest, VisionResponse

logger = get_logger(__name__)


class LMStudioBackend:
    name = "lm_studio"

    def __init__(
        self,
        primary_url: str,
        primary_model: str,
        *,
        secondary_url: str | None = None,
        secondary_model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
        retry_min_wait: int | None = None,
        retry_max_wait: int | None = None,
    ) -> None:
        self._primary_url = primary_url
        self._primary_model = primary_model
        self._secondary_url = secondary_url
        self._secondary_model = secondary_model
        self._client_kwargs = {
            k: v
            for k, v in {
                'max_tokens': max_tokens,
                'temperature': temperature,
                'timeout': timeout,
                'max_retries': max_retries,
                'retry_min_wait': retry_min_wait,
                'retry_max_wait': retry_max_wait,
            }.items()
            if v is not None
        }
        self._clients: dict[VLMRole, LMStudioClient] = {}

    def capabilities(self) -> BackendCapabilities:
        is_dual = bool(self._secondary_url and self._secondary_model)
        notes: list[str] = []
        if not is_dual:
            notes.append('secondary endpoint not configured; dual-VLM disabled')
        return BackendCapabilities(
            name=self.name,
            supports_dual_vlm=is_dual,
            supports_constrained_decoding=True,
            supports_logprobs=False,
            supports_multi_image=True,
            supports_tensor_parallelism=False,
            notes=tuple(notes),
        )

    def resolve(self, role: VLMRole) -> tuple[str, str]:
        if role in (VLMRole.PRIMARY, VLMRole.LITE):
            return self._primary_url, self._primary_model
        if role in (VLMRole.SECONDARY, VLMRole.CRITIC):
            if self._secondary_url and self._secondary_model:
                return self._secondary_url, self._secondary_model
            logger.debug('lm_studio_role_collapsed_to_primary', requested_role=role.value)
            return self._primary_url, self._primary_model
        raise ValueError(f'Unknown VLMRole: {role!r}')

    def health(self) -> BackendHealth:
        roles_to_probe: list[VLMRole] = [VLMRole.PRIMARY]
        if self._secondary_url and self._secondary_model:
            roles_to_probe.append(VLMRole.SECONDARY)

        results: dict[VLMRole, dict[str, Any]] = {}
        overall = True
        for role in roles_to_probe:
            url, model = self.resolve(role)
            client = self._get_client(role)
            t0 = time.perf_counter()
            try:
                healthy = client.is_healthy()
                detail = {
                    'healthy': healthy,
                    'base_url': url,
                    'model': model,
                    'latency_ms': int((time.perf_counter() - t0) * 1000),
                }
            except Exception as exc:
                healthy = False
                detail = {
                    'healthy': False,
                    'base_url': url,
                    'model': model,
                    'latency_ms': int((time.perf_counter() - t0) * 1000),
                    'error': str(exc),
                }
            results[role] = detail
            overall = overall and healthy
        return BackendHealth(backend_name=self.name, overall_healthy=overall, roles=results)

    def send_vision_request(
        self,
        request: 'VisionRequest',
        *,
        role: VLMRole = VLMRole.PRIMARY,
        schema: dict[str, Any] | None = None,
    ) -> 'VisionResponse':
        client = self._get_client(role)
        _, model = self.resolve(role)
        response_format = None
        if schema is not None:
            response_format = {
                'type': 'json_schema',
                'json_schema': {'name': 'veridoc', 'schema': schema},
            }
        return client.send_vision_request(
            request,
            model=model,
            response_format=response_format,
        )

    async def send_vision_request_async(
        self,
        request: 'VisionRequest',
        *,
        role: VLMRole = VLMRole.PRIMARY,
        schema: dict[str, Any] | None = None,
    ) -> 'VisionResponse':
        client = self._get_client(role)
        _, model = self.resolve(role)
        response_format = None
        if schema is not None:
            response_format = {
                'type': 'json_schema',
                'json_schema': {'name': 'veridoc', 'schema': schema},
            }
        return await client.send_vision_request_async(
            request,
            model=model,
            response_format=response_format,
        )

    def close(self) -> None:
        for client in self._clients.values():
            try:
                client.close()
            except Exception:
                pass
        self._clients.clear()

    def _get_client(self, role: VLMRole) -> LMStudioClient:
        if role not in self._clients:
            url, model = self.resolve(role)
            self._clients[role] = LMStudioClient(base_url=url, model=model, **self._client_kwargs)
        return self._clients[role]


assert isinstance(LMStudioBackend('http://localhost:1234/v1', 'qwen3-vl'), VLMBackend)
