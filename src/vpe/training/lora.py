"""Brand LoRA training metadata entry point."""

from __future__ import annotations

from pathlib import Path

from vpe.core.lora import BrandLoRAAdapter, BrandLoRARegistry


def create_brand_lora_adapter(
    brand_id: str,
    rank: int,
    adapter_path: Path,
    registry: BrandLoRARegistry | None = None,
) -> Path:
    """Register a brand LoRA adapter produced by training."""

    selected_registry = registry or BrandLoRARegistry()
    return selected_registry.register(BrandLoRAAdapter(brand_id=brand_id, rank=rank, path=adapter_path))
