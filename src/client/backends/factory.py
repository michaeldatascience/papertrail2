"""Factory for selecting the configured VLM backend."""

from __future__ import annotations

from src.client.backends.lm_studio_backend import LMStudioBackend
from src.client.backends.vllm_backend import VLLMBackend
from src.config import get_settings


def get_backend():
    settings = get_settings()
    backend_name = settings.vlm.backend.value

    if backend_name == 'vllm':
        cfg = settings.vlm.vllm
        return VLLMBackend(
            primary_url=cfg.primary_url,
            primary_model=cfg.primary_model,
            secondary_url=cfg.secondary_url,
            secondary_model=cfg.secondary_model,
            guided_decoding_backend=cfg.guided_decoding_backend,
            max_tokens=settings.lm_studio.max_tokens,
            temperature=settings.lm_studio.temperature,
            timeout=settings.lm_studio.timeout,
            max_retries=settings.lm_studio.max_retries,
            retry_min_wait=settings.lm_studio.retry_min_wait,
            retry_max_wait=settings.lm_studio.retry_max_wait,
        )

    lm_cfg = settings.vlm.lm_studio
    primary_url = lm_cfg.primary_url or str(settings.lm_studio.base_url)
    primary_model = lm_cfg.primary_model or settings.lm_studio.model
    secondary_url = lm_cfg.secondary_url
    secondary_model = lm_cfg.secondary_model

    return LMStudioBackend(
        primary_url=primary_url,
        primary_model=primary_model,
        secondary_url=secondary_url,
        secondary_model=secondary_model,
        max_tokens=settings.lm_studio.max_tokens,
        temperature=settings.lm_studio.temperature,
        timeout=settings.lm_studio.timeout,
        max_retries=settings.lm_studio.max_retries,
        retry_min_wait=settings.lm_studio.retry_min_wait,
        retry_max_wait=settings.lm_studio.retry_max_wait,
    )
