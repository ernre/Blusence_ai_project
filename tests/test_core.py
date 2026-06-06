from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from vpe.core import DecoupledCrossAttention, GarmentEncoder, VPEngine
from vpe.types import TryOnRequest


def _image(path: Path, color: str) -> Path:
    Image.new("RGB", (8, 8), color).save(path)
    return path


def _mask(path: Path) -> Path:
    Image.new("L", (8, 8), 255).save(path)
    return path


def test_garment_encoder_returns_projected_features(tmp_path: Path) -> None:
    garment = _image(tmp_path / "garment.png", "green")

    features = GarmentEncoder(projection_dim=12, image_size=8).encode(garment)

    assert features.embedding.shape == (12,)
    assert np.isclose(np.linalg.norm(features.embedding), 1.0)


def test_decoupled_attention_validates_shape() -> None:
    with pytest.raises(ValueError, match="latent"):
        DecoupledCrossAttention().apply(np.zeros((3,)), np.zeros((3,)))


def test_engine_renders_tryon(tmp_path: Path) -> None:
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")
    mask = _mask(tmp_path / "mask.png")

    result = VPEngine(output_dir=tmp_path, image_size=8).render(
        TryOnRequest(person_image=person, garment_image=garment, mask_image=mask)
    )

    assert result.image_path.exists()
    assert result.metadata["garment_backbone"] == "stub"
