"""Evaluation CLI."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from vpe.eval.metrics import compare_images


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate VPE outputs")
    parser.add_argument("--prediction", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--image-size", type=int, default=256)
    args = parser.parse_args()

    result = compare_images(Path(args.prediction), Path(args.reference), args.image_size)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
