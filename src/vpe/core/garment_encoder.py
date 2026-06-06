"""Garment feature encoding and projection components."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from vpe.utils.images import load_rgb


@dataclass(frozen=True)
class GarmentFeatures:
    """Projected garment conditioning features."""

    embedding: np.ndarray
    backbone: str


class GarmentEncoder:
    """DINOv2/CLIP-style garment encoder facade with a deterministic stub mode."""

    def __init__(self, backbone: str = "stub", projection_dim: int = 768, image_size: int = 256) -> None:
        self.backbone = backbone
        self.projection_dim = projection_dim
        self.image_size = image_size
        if backbone != "stub":
            raise NotImplementedError(
                "Only the stub garment encoder is available without optional ML dependencies"
            )

    def encode(self, garment_image: Path) -> GarmentFeatures:
        """Encode a garment image into a projected conditioning vector."""

        image = load_rgb(garment_image, self.image_size)
        pixels = np.asarray(image, dtype=np.float32) / 255.0
        channel_stats = np.concatenate(
            [pixels.mean(axis=(0, 1)), pixels.std(axis=(0, 1)), pixels.max(axis=(0, 1))]
        )
        repeated = np.resize(channel_stats, self.projection_dim).astype(np.float32)
        norm = np.linalg.norm(repeated)
        embedding = repeated / norm if norm else repeated
        return GarmentFeatures(embedding=embedding, backbone=self.backbone)
