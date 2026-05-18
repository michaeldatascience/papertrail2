"""Minimal document-profile registry."""

from __future__ import annotations

from dataclasses import dataclass

from src.profiles.descriptor import ProfileDescriptor


@dataclass(frozen=True, slots=True)
class ProfileDetectionResult:
    profile_name: str
    confidence: float
    score_by_profile: dict[str, float]
    matched_signals: dict[str, list[str]]
    fallback_to_generic: bool = False


_GENERIC = ProfileDescriptor(
    name='generic-document',
    display_name='Generic Document',
    description='Fallback profile for non-specialised documents.',
    confidence_floor=0.0,
)

_MEDICAL_RCM = ProfileDescriptor(
    name='medical-rcm',
    display_name='Medical RCM',
    description='Healthcare revenue-cycle documents.',
    confidence_floor=0.5,
    schema_overlay_fields=('healthcare_core',),
)

_PROFILES = {
    _GENERIC.name: _GENERIC,
    _MEDICAL_RCM.name: _MEDICAL_RCM,
}

_MEDICAL_HINTS = (
    'cpt', 'icd', 'npi', 'claim', 'patient', 'provider', 'diagnosis', 'superbill', 'cms-1500', 'ub-04', 'eob'
)


def get_profile(name: str) -> ProfileDescriptor:
    return _PROFILES.get(name, _GENERIC)


def detect_profile(
    *,
    classification_features: list[str] | None = None,
    page_text: str = '',
    document_type: str | None = None,
    profile_override: str | None = None,
) -> ProfileDetectionResult:
    if profile_override:
        name = profile_override if profile_override in _PROFILES else _GENERIC.name
        return ProfileDetectionResult(
            profile_name=name,
            confidence=1.0,
            score_by_profile={name: 1.0},
            matched_signals={name: ['profile_override']},
            fallback_to_generic=False,
        )

    haystack = ' '.join(classification_features or []) + ' ' + page_text + ' ' + (document_type or '')
    lowered = haystack.lower()
    matched = [hint for hint in _MEDICAL_HINTS if hint in lowered]
    if matched:
        return ProfileDetectionResult(
            profile_name=_MEDICAL_RCM.name,
            confidence=min(0.95, 0.55 + 0.05 * len(matched)),
            score_by_profile={_MEDICAL_RCM.name: 0.9, _GENERIC.name: 0.1},
            matched_signals={_MEDICAL_RCM.name: matched},
            fallback_to_generic=False,
        )

    return ProfileDetectionResult(
        profile_name=_GENERIC.name,
        confidence=1.0,
        score_by_profile={_GENERIC.name: 1.0},
        matched_signals={_GENERIC.name: ['fallback_generic']},
        fallback_to_generic=False,
    )


__all__ = ['ProfileDescriptor', 'ProfileDetectionResult', 'detect_profile', 'get_profile']
