from pathlib import Path

from PIL import Image

from vpe.core import CrossViewAttentionBlock, PoseConditioner, VPEngine
from vpe.types import TryOnRequest


def _image(path: Path, color: str) -> Path:
    Image.new("RGB", (8, 8), color).save(path)
    return path


def _mask(path: Path) -> Path:
    Image.new("L", (8, 8), 255).save(path)
    return path


def test_pose_conditioner_returns_zero_without_pose() -> None:
    tokens = PoseConditioner(image_size=8).tokens(None)

    assert tokens.tolist() == [0.0, 0.0, 0.0]


def test_cross_view_block_noops_without_views() -> None:
    import numpy as np

    latent = np.ones((2, 2, 3), dtype=np.float32)

    assert CrossViewAttentionBlock(image_size=8).apply(latent, ()) is latent


def test_engine_records_pose_and_multiview_metadata(tmp_path: Path) -> None:
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")
    mask = _mask(tmp_path / "mask.png")
    pose = _image(tmp_path / "pose.png", "black")
    side_view = _image(tmp_path / "side.png", "gray")

    result = VPEngine(output_dir=tmp_path, image_size=8).render(
        TryOnRequest(
            person_image=person,
            garment_image=garment,
            mask_image=mask,
            pose_image=pose,
            person_views=(side_view,),
        )
    )

    assert result.image_path.exists()
    assert result.metadata["view_count"] == 2
    assert result.metadata["pose_conditioned"] is True
