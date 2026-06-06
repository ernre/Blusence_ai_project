"""Brand-level LoRA adapter registry and loader."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrandLoRAAdapter:
    """Metadata for a brand-specific LoRA adapter."""

    brand_id: str
    rank: int
    path: Path
    scale: float = 1.0


class BrandLoRARegistry:
    """Filesystem registry for brand LoRA adapters."""

    def __init__(self, root: Path = Path("artifacts/lora")) -> None:
        self.root = root

    def register(self, adapter: BrandLoRAAdapter) -> Path:
        """Write adapter metadata for a brand."""

        if not 8 <= adapter.rank <= 32:
            raise ValueError("Brand LoRA rank must be between 8 and 32")
        brand_dir = self.root / adapter.brand_id
        brand_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = brand_dir / "adapter.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "brand_id": adapter.brand_id,
                    "rank": adapter.rank,
                    "path": str(adapter.path),
                    "scale": adapter.scale,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return metadata_path

    def load(self, brand_id: str) -> BrandLoRAAdapter:
        """Load adapter metadata for a brand."""

        metadata_path = self.root / brand_id / "adapter.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Brand LoRA adapter is not registered: {brand_id}")
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        return BrandLoRAAdapter(
            brand_id=str(payload["brand_id"]),
            rank=int(payload["rank"]),
            path=Path(str(payload["path"])),
            scale=float(payload.get("scale", 1.0)),
        )


class BrandLoRALoader:
    """Runtime LoRA loader seam for PEFT-backed brand adaptation."""

    def __init__(self, registry: BrandLoRARegistry | None = None) -> None:
        self.registry = registry or BrandLoRARegistry()

    def resolve(self, brand_id: str | None) -> BrandLoRAAdapter | None:
        """Resolve a brand adapter if one is requested."""

        if brand_id is None:
            return None
        return self.registry.load(brand_id)
