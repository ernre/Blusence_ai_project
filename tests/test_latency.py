from pathlib import Path

import pytest
from PIL import Image

from vpe.latency import LatencyOptimizationPlan, export_tensorrt_stub, run_benchmark
from vpe.types import TryOnRequest


def _image(path: Path, color: str, mode: str = "RGB") -> Path:
    Image.new(mode, (8, 8), color).save(path)
    return path


def test_latency_plan_validates_sampling_steps() -> None:
    with pytest.raises(ValueError, match="4-8"):
        LatencyOptimizationPlan(2, "fp16", True, "none", False).validate()


def test_benchmark_runs(tmp_path: Path) -> None:
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")
    mask = _image(tmp_path / "mask.png", "white", mode="L")

    result = run_benchmark(
        TryOnRequest(person_image=person, garment_image=garment, mask_image=mask),
        runs=2,
        image_size=8,
    )

    assert result.runs == 2
    assert result.mean_seconds >= 0


def test_tensorrt_export_stub_writes_manifest(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text("{}", encoding="utf-8")

    output = export_tensorrt_stub(checkpoint, tmp_path / "engine.plan.txt")

    assert output.exists()
