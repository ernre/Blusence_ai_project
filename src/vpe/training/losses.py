"""Training loss helpers."""

from __future__ import annotations

from pathlib import Path

from vpe.utils.images import load_rgb, mean_abs_difference


def reconstruction_loss(prediction: Path, target: Path, image_size: int = 256) -> float:
    """CPU-friendly L1 reconstruction proxy."""

    left = load_rgb(prediction, image_size)
    right = load_rgb(target, image_size)
    return mean_abs_difference(left, right) / 255.0


def perceptual_loss_proxy(prediction: Path, target: Path, image_size: int = 256) -> float:
    """Placeholder for LPIPS/perceptual loss that is deterministic on CPU."""

    return reconstruction_loss(prediction, target, image_size) * 0.5


def texture_loss_proxy(prediction: Path, target: Path, image_size: int = 256) -> float:
    """Placeholder for garment texture preservation loss."""

    return reconstruction_loss(prediction, target, image_size) * 0.25
