"""FASHN.ai benchmark provider."""

from __future__ import annotations

from vpe.baseline.fashn import FashnBaselineVTON, FashnConfig
from vpe.providers.base import ProviderDescriptor
from vpe.types import TryOnRequest, TryOnResult


class FashnBenchmarkProvider(FashnBaselineVTON):
    """External FASHN.ai provider for launch acceleration and quality benchmarking."""

    descriptor = ProviderDescriptor(
        id="fashn",
        label="FASHN.ai benchmark",
        role="external-benchmark",
        status="requires-api-key",
        requires=("FASHN_API_KEY",),
        notes=(
            "Use for paid external baseline runs and side-by-side evaluation. "
            "Do not treat outputs as proprietary model training data unless terms allow it."
        ),
    )

    def render(self, request: TryOnRequest) -> TryOnResult:
        result = super().render(request)
        return TryOnResult(
            image_path=result.image_path,
            engine=result.engine,
            metadata={
                **result.metadata,
                "provider_id": self.descriptor.id,
                "provider_role": self.descriptor.role,
            },
        )


__all__ = ["FashnBenchmarkProvider", "FashnConfig"]
