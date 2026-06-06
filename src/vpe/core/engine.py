"""VPE inference engine facade."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from vpe.core.attention import DecoupledCrossAttention
from vpe.core.garment_encoder import GarmentEncoder
from vpe.core.multiview import CrossViewAttentionBlock
from vpe.core.pose import PoseConditioner
from vpe.types import TryOnRequest, TryOnResult
from vpe.utils.images import composite_garment, load_mask, load_rgb


class VPEngine:
    """Production-facing try-on engine.

    The default `stub` provider is CPU-friendly and deterministic for tests. A
    diffusers provider can be wired behind this facade when optional ML
    dependencies and model weights are configured.
    """

    def __init__(
        self,
        output_dir: Path = Path("outputs/vpe"),
        provider: str = "stub",
        image_size: int = 256,
        garment_encoder: GarmentEncoder | None = None,
        attention: DecoupledCrossAttention | None = None,
        pose_conditioner: PoseConditioner | None = None,
        cross_view_block: CrossViewAttentionBlock | None = None,
    ) -> None:
        self.output_dir = output_dir
        self.provider = provider
        self.image_size = image_size
        self.garment_encoder = garment_encoder or GarmentEncoder(image_size=image_size)
        self.attention = attention or DecoupledCrossAttention(scale=0.05)
        self.pose_conditioner = pose_conditioner or PoseConditioner(image_size=image_size)
        self.cross_view_block = cross_view_block or CrossViewAttentionBlock(image_size=image_size)
        if provider != "stub":
            raise NotImplementedError(
                "Configure optional diffusers dependencies before using non-stub providers"
            )

    def render(self, request: TryOnRequest) -> TryOnResult:
        """Render a try-on image from person, garment, and mask inputs."""

        if request.mask_image is None:
            raise ValueError("VPEngine requires mask_image for inpainting")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        person = load_rgb(request.person_image, self.image_size)
        garment = load_rgb(request.garment_image, self.image_size)
        mask = load_mask(request.mask_image, self.image_size)
        features = self.garment_encoder.encode(request.garment_image)
        conditioned = self._condition_garment(
            garment,
            features.embedding,
            request.pose_image,
            request.person_views,
        )
        output = composite_garment(person, conditioned, mask)
        output_path = self.output_dir / "vpe-tryon.png"
        output.save(output_path)
        return TryOnResult(
            image_path=output_path,
            engine="vpe-stub-inpaint",
            metadata={
                "provider": self.provider,
                "garment_backbone": features.backbone,
                "image_size": self.image_size,
                "view_count": len(request.person_views) + 1,
                "pose_conditioned": request.pose_image is not None,
            },
        )

    def _condition_garment(
        self,
        garment: Image.Image,
        embedding: np.ndarray,
        pose_image: Path | None,
        person_views: tuple[Path, ...],
    ) -> Image.Image:
        latent = np.asarray(garment, dtype=np.float32) / 255.0
        conditioned = self.attention.apply(latent, embedding)
        conditioned = self.pose_conditioner.apply(conditioned, pose_image)
        conditioned = self.cross_view_block.apply(conditioned, person_views)
        clipped = np.clip(conditioned, 0.0, 1.0)
        return Image.fromarray((clipped * 255).astype(np.uint8), mode="RGB")
