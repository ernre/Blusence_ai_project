"""Decoupled cross-attention utilities for garment conditioning."""

from __future__ import annotations

import numpy as np


class DecoupledCrossAttention:
    """Small NumPy attention block mirroring an IP-Adapter-style conditioning seam."""

    def __init__(self, scale: float = 1.0) -> None:
        self.scale = scale

    def apply(self, latent: np.ndarray, garment_embedding: np.ndarray) -> np.ndarray:
        """Inject garment information into a latent tensor."""

        if latent.ndim != 3:
            raise ValueError("latent must have shape [height, width, channels]")
        if garment_embedding.ndim != 1:
            raise ValueError("garment_embedding must be a flat vector")
        channels = latent.shape[-1]
        projected = np.resize(garment_embedding, channels).reshape(1, 1, channels)
        return latent + (projected * self.scale)
