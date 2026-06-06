"""Multi-view consistency components."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from vpe.utils.images import load_rgb


class CrossViewAttentionBlock:
    """Cross-view aggregation seam for shared garment consistency."""

    def __init__(self, image_size: int = 256, strength: float = 0.1) -> None:
        self.image_size = image_size
        self.strength = strength

    def apply(self, latent: np.ndarray, person_views: tuple[Path, ...]) -> np.ndarray:
        """Blend a latent with compact statistics from additional views."""

        if not person_views:
            return latent
        view_stats = []
        for view in person_views:
            image = load_rgb(view, self.image_size)
            view_stats.append(np.asarray(image, dtype=np.float32).mean(axis=(0, 1)) / 255.0)
        mean_view = np.mean(np.stack(view_stats, axis=0), axis=0).reshape(1, 1, 3)
        return np.clip(latent * (1.0 - self.strength) + mean_view * self.strength, 0.0, 1.0)
