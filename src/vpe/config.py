"""Configuration loading and reproducibility helpers."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from omegaconf import OmegaConf


@dataclass(frozen=True)
class RuntimeContext:
    """Metadata logged by each deterministic run."""

    config_hash: str
    git_sha: str
    dataset_version: str
    seed: int


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML config as a plain dictionary."""

    config = OmegaConf.load(path)
    return OmegaConf.to_container(config, resolve=True)  # type: ignore[return-value]


def config_hash(config: dict[str, Any]) -> str:
    """Return a stable hash for a config dictionary."""

    encoded = json.dumps(config, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:12]


def seed_everything(seed: int) -> None:
    """Seed standard CPU randomness sources."""

    random.seed(seed)
    np.random.seed(seed)


def runtime_context(config: dict[str, Any], git_sha: str) -> RuntimeContext:
    """Build run metadata from config and git revision."""

    seed = int(config["engine"]["seed"])
    return RuntimeContext(
        config_hash=config_hash(config),
        git_sha=git_sha,
        dataset_version=str(config["data"]["dataset_version"]),
        seed=seed,
    )
