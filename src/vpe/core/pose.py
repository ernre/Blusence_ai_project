"""Pose-aware conditioning components."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from vpe.utils.images import load_rgb


class PoseConditioner:
    """ControlNet-style pose conditioning facade.

    Stub mode converts a pose image into a compact token that can be injected
    into the image latent. Real DensePose/OpenPose providers should implement
    the same token contract.
    """

    def __init__(self, provider: str = "stub", image_size: int = 256, strength: float = 0.05) -> None:
        self.provider = provider
        self.image_size = image_size
        self.strength = strength
        if provider != "stub":
            raise NotImplementedError("Only stub pose conditioning is available without pose deps")

    def tokens(self, pose_image: Path | None) -> np.ndarray:
        """Return pose tokens for optional pose input."""

        if pose_image is None:
            return np.zeros((3,), dtype=np.float32)
        image = load_rgb(pose_image, self.image_size)
        pixels = np.asarray(image, dtype=np.float32) / 255.0
        return pixels.mean(axis=(0, 1)).astype(np.float32)

    def apply(self, latent: np.ndarray, pose_image: Path | None) -> np.ndarray:
        """Inject pose tokens into an RGB latent."""

        token = self.tokens(pose_image).reshape(1, 1, 3)
        return np.clip(latent + token * self.strength, 0.0, 1.0)
