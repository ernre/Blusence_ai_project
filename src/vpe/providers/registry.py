"""Provider registry for serving and product introspection."""

from __future__ import annotations

import os
from pathlib import Path

from vpe.providers.base import ProviderDescriptor, ProviderUnavailableError, TryOnProvider
from vpe.providers.fashn import FashnBenchmarkProvider, FashnConfig
from vpe.providers.idm_vton import IDMVTONConfig, IDMVTONResearchProvider
from vpe.providers.local import LocalPreviewProvider

_ALIASES = {
    "preview": "local",
    "stub": "local",
    "fashn_ai": "fashn",
    "fashn.ai": "fashn",
    "idm": "idm_vton",
    "idm-vton": "idm_vton",
}


def active_provider_id() -> str:
    """Return the normalized active provider id from the environment."""

    return normalize_provider_id(os.getenv("VPE_TRYON_PROVIDER", "local"))


def normalize_provider_id(provider_id: str) -> str:
    """Normalize CLI/env aliases to stable provider identifiers."""

    value = provider_id.strip().lower()
    return _ALIASES.get(value, value)


def provider_descriptors() -> list[ProviderDescriptor]:
    """Return product-visible provider metadata."""

    return [
        LocalPreviewProvider.descriptor,
        FashnBenchmarkProvider.descriptor,
        IDMVTONResearchProvider.descriptor,
    ]


def build_tryon_provider(provider_id: str, output_dir: Path, image_size: int = 256) -> TryOnProvider:
    """Build a provider for the requested id."""

    normalized = normalize_provider_id(provider_id)
    if normalized == "local":
        return LocalPreviewProvider(output_dir=output_dir, image_size=image_size)
    if normalized == "fashn":
        return FashnBenchmarkProvider(FashnConfig.from_env())
    if normalized == "idm_vton":
        return IDMVTONResearchProvider(IDMVTONConfig.from_env(output_dir=output_dir))
    raise ProviderUnavailableError(f"Unknown VPE_TRYON_PROVIDER: {provider_id}")
