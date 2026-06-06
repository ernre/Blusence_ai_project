"""Latency benchmark CLI."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from vpe.core import VPEngine
from vpe.types import TryOnRequest


@dataclass(frozen=True)
class BenchmarkResult:
    """Latency benchmark result."""

    runs: int
    mean_seconds: float
    p95_seconds: float
    engine: str


def run_benchmark(request: TryOnRequest, runs: int = 3, image_size: int = 256) -> BenchmarkResult:
    """Run a local deterministic inference benchmark."""

    if runs < 1:
        raise ValueError("runs must be >= 1")
    engine = VPEngine(output_dir=Path("outputs/latency"), image_size=image_size)
    timings: list[float] = []
    last_engine = ""
    for _ in range(runs):
        start = time.perf_counter()
        result = engine.render(request)
        timings.append(time.perf_counter() - start)
        last_engine = result.engine
    sorted_timings = sorted(timings)
    p95_index = min(len(sorted_timings) - 1, int(round((len(sorted_timings) - 1) * 0.95)))
    return BenchmarkResult(
        runs=runs,
        mean_seconds=sum(timings) / len(timings),
        p95_seconds=sorted_timings[p95_index],
        engine=last_engine,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark VPE inference latency")
    parser.add_argument("--person-image", required=True)
    parser.add_argument("--garment-image", required=True)
    parser.add_argument("--mask-image", required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--image-size", type=int, default=256)
    args = parser.parse_args()

    result = run_benchmark(
        TryOnRequest(
            person_image=Path(args.person_image),
            garment_image=Path(args.garment_image),
            mask_image=Path(args.mask_image),
        ),
        runs=args.runs,
        image_size=args.image_size,
    )
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
