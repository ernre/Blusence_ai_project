"""Training CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vpe.config import load_config
from vpe.training.trainer import Trainer


def main() -> None:
    parser = argparse.ArgumentParser(description="Run VPE training")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--output-dir", default="outputs/training")
    args = parser.parse_args()

    summary = Trainer(load_config(args.config), output_dir=Path(args.output_dir)).run()
    print(json.dumps(summary.__dict__, indent=2))


if __name__ == "__main__":
    main()
