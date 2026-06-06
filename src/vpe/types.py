"""Shared typed request and response objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class TryOnRequest:
    """Inputs needed to render a virtual try-on."""

    person_image: Path
    garment_image: Path
    mask_image: Path | None = None
    pose_image: Path | None = None
    person_views: tuple[Path, ...] = field(default_factory=tuple)
    category: str | None = None
    brand_id: str | None = None
    seed: int | None = None


@dataclass(frozen=True)
class TryOnResult:
    """Rendered try-on output plus provenance."""

    image_path: Path
    engine: str
    metadata: dict[str, str | int | float | bool]
