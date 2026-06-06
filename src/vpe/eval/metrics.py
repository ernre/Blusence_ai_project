"""Automatic evaluation metrics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vpe.utils.images import load_rgb, mean_abs_difference


@dataclass(frozen=True)
class MetricResult:
    """Image comparison metrics."""

    mae: float
    similarity: float


def compare_images(prediction: Path, reference: Path, image_size: int = 256) -> MetricResult:
    """Compute deterministic CPU image metrics."""

    pred = load_rgb(prediction, image_size)
    ref = load_rgb(reference, image_size)
    mae = mean_abs_difference(pred, ref) / 255.0
    return MetricResult(mae=mae, similarity=max(0.0, 1.0 - mae))
