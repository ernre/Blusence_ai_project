"""Local product preview provider."""

from __future__ import annotations

from pathlib import Path

from vpe.core import VPEngine
from vpe.providers.base import ProviderDescriptor, TryOnProvider
from vpe.types import TryOnRequest, TryOnResult


class LocalPreviewProvider(TryOnProvider):
    """CPU-runnable product provider used for smoke tests and local demos."""

    descriptor = ProviderDescriptor(
        id="local",
        label="Local preview compositor",
        role="product-preview",
        status="available",
        notes=(
            "Deterministic offline renderer for product flow validation. "
            "It is not the final generative VTON model."
        ),
    )

    def __init__(self, output_dir: Path, image_size: int = 256) -> None:
        self._engine = VPEngine(output_dir=output_dir, image_size=image_size)

    def render(self, request: TryOnRequest) -> TryOnResult:
        result = self._engine.render(request)
        return TryOnResult(
            image_path=result.image_path,
            engine=result.engine,
            metadata={
                **result.metadata,
                "provider_id": self.descriptor.id,
                "provider_role": self.descriptor.role,
            },
        )
