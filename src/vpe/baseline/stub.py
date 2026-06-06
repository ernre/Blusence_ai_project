"""Deterministic offline baseline for tests and local smoke runs."""

from __future__ import annotations

from pathlib import Path

from vpe.baseline.base import BaselineVTON
from vpe.types import TryOnRequest, TryOnResult
from vpe.utils.images import composite_garment, load_mask, load_rgb


class StubBaselineVTON(BaselineVTON):
    """Simple compositor that mimics the baseline interface without network IO."""

    def __init__(self, output_dir: Path = Path("outputs/baseline_stub"), image_size: int = 256) -> None:
        self._output_dir = output_dir
        self._image_size = image_size

    def render(self, request: TryOnRequest) -> TryOnResult:
        if request.mask_image is None:
            raise ValueError("StubBaselineVTON requires mask_image")
        self._output_dir.mkdir(parents=True, exist_ok=True)
        person = load_rgb(request.person_image, self._image_size)
        garment = load_rgb(request.garment_image, self._image_size)
        mask = load_mask(request.mask_image, self._image_size)
        result = composite_garment(person, garment, mask)
        output = self._output_dir / "stub-baseline.png"
        result.save(output)
        return TryOnResult(
            image_path=output,
            engine="stub-baseline",
            metadata={"image_size": self._image_size},
        )
