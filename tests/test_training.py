from pathlib import Path

from PIL import Image

from vpe.config import load_config
from vpe.data import VTONDataset
from vpe.training import Trainer


def _ensure_smoke_images() -> None:
    root = Path("tests/smoke_dataset")
    colors = {
        "person.png": "white",
        "garment.png": "red",
        "mask.png": "white",
        "pose.png": "black",
        "target.png": "red",
    }
    for name, color in colors.items():
        mode = "L" if name == "mask.png" else "RGB"
        Image.new(mode, (8, 8), color).save(root / name)


def test_dataset_loads_manifest() -> None:
    _ensure_smoke_images()

    dataset = VTONDataset(Path("tests/smoke_dataset"))

    assert len(dataset) == 1
    assert dataset[0].brand_id == "demo-brand"


def test_trainer_writes_checkpoint(tmp_path: Path) -> None:
    _ensure_smoke_images()
    config = load_config("configs/base.yaml")
    config["model"]["image_size"] = 8

    summary = Trainer(config, output_dir=tmp_path).run()

    assert summary.samples == 1
    assert Path(summary.checkpoint_path).exists()
