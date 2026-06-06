"""Config-driven training loop for VPE smoke and adapter training."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from vpe.config import config_hash, seed_everything
from vpe.core import VPEngine
from vpe.data.dataset import VTONDataset
from vpe.training.losses import perceptual_loss_proxy, reconstruction_loss, texture_loss_proxy


@dataclass(frozen=True)
class TrainingSummary:
    """Serializable training run summary."""

    samples: int
    mean_loss: float
    config_hash: str
    checkpoint_path: str


class Trainer:
    """Small trainer that exercises the full data/model/loss/checkpoint path."""

    def __init__(self, config: dict[str, object], output_dir: Path = Path("outputs/training")) -> None:
        self.config = config
        self.output_dir = output_dir

    def run(self) -> TrainingSummary:
        engine_config = self.config["engine"]  # type: ignore[index]
        data_config = self.config["data"]  # type: ignore[index]
        model_config = self.config["model"]  # type: ignore[index]
        seed_everything(int(engine_config["seed"]))
        dataset = VTONDataset(Path(str(data_config["root"])))
        image_size = int(model_config["image_size"])
        engine = VPEngine(output_dir=self.output_dir / "renders", image_size=image_size)
        losses: list[float] = []
        for item in dataset:
            if item.target_image is None:
                continue
            result = engine.render(item.request)
            loss = (
                reconstruction_loss(result.image_path, item.target_image, image_size)
                + perceptual_loss_proxy(result.image_path, item.target_image, image_size)
                + texture_loss_proxy(result.image_path, item.target_image, image_size)
            )
            losses.append(loss)
        mean_loss = sum(losses) / len(losses) if losses else 0.0
        self.output_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_path = self.output_dir / "checkpoint.json"
        summary = TrainingSummary(
            samples=len(dataset),
            mean_loss=mean_loss,
            config_hash=config_hash(self.config),  # type: ignore[arg-type]
            checkpoint_path=str(checkpoint_path),
        )
        checkpoint_path.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")
        return summary
