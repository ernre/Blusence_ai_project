"""Latency optimization configuration and guards."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LatencyOptimizationPlan:
    """Inference acceleration choices for a run."""

    sampling_steps: int
    dtype: str
    compile_model: bool
    quantization: str
    tensorrt: bool

    def validate(self) -> None:
        if not 4 <= self.sampling_steps <= 8:
            raise ValueError("Latency target expects 4-8 sampling steps")
        if self.dtype not in {"fp16", "bf16", "fp32"}:
            raise ValueError("dtype must be one of fp16, bf16, fp32")
        if self.quantization not in {"none", "int8"}:
            raise ValueError("quantization must be none or int8")


def export_tensorrt_stub(checkpoint: Path, output_path: Path) -> Path:
    """Create a manifest for the TensorRT export path without exporting weights."""

    if not checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint does not exist: {checkpoint}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "TensorRT export requires optional GPU dependencies and model weights.\n",
        encoding="utf-8",
    )
    return output_path
