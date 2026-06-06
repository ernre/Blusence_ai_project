"""Dataset loading for VPE training and smoke tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from vpe.types import TryOnRequest


@dataclass(frozen=True)
class DatasetItem:
    """A single VTON training sample."""

    sample_id: str
    request: TryOnRequest
    target_image: Path | None
    brand_id: str | None


class VTONDataset:
    """Manifest-backed dataset with strict path validation."""

    def __init__(self, root: Path, manifest_name: str = "manifest.jsonl") -> None:
        self.root = root
        self.manifest_path = root / manifest_name
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Dataset manifest not found: {self.manifest_path}")
        self._items = [self._parse(line) for line in self.manifest_path.read_text().splitlines() if line]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[DatasetItem]:
        return iter(self._items)

    def __getitem__(self, index: int) -> DatasetItem:
        return self._items[index]

    def _parse(self, line: str) -> DatasetItem:
        payload = json.loads(line)
        sample_id = str(payload["sample_id"])
        person = self._resolve(payload["person_image"])
        garment = self._resolve(payload["garment_image"])
        mask = self._resolve(payload.get("mask_image"))
        pose = self._resolve(payload.get("pose_image"))
        target = self._resolve(payload.get("target_image"))
        request = TryOnRequest(
            person_image=person,
            garment_image=garment,
            mask_image=mask,
            pose_image=pose,
            brand_id=payload.get("brand_id"),
        )
        return DatasetItem(sample_id=sample_id, request=request, target_image=target, brand_id=payload.get("brand_id"))

    def _resolve(self, value: str | None) -> Path | None:
        if value is None:
            return None
        path = self.root / value
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")
        return path
