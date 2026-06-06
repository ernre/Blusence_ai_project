from pathlib import Path

import pytest

from vpe.core import BrandLoRAAdapter, BrandLoRALoader, BrandLoRARegistry, VPEngine
from vpe.training.lora import create_brand_lora_adapter
from vpe.types import TryOnRequest


def test_lora_registry_round_trips(tmp_path: Path) -> None:
    registry = BrandLoRARegistry(tmp_path)
    adapter = BrandLoRAAdapter(brand_id="brand-a", rank=16, path=Path("adapter.safetensors"))

    metadata = registry.register(adapter)
    loaded = registry.load("brand-a")

    assert metadata.exists()
    assert loaded.rank == 16


def test_lora_registry_rejects_invalid_rank(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="rank"):
        BrandLoRARegistry(tmp_path).register(
            BrandLoRAAdapter(brand_id="brand-a", rank=4, path=Path("adapter.safetensors"))
        )


def test_engine_resolves_brand_lora(tmp_path: Path) -> None:
    from PIL import Image

    registry = BrandLoRARegistry(tmp_path / "lora")
    create_brand_lora_adapter("demo-brand", 8, Path("demo.safetensors"), registry)
    person = tmp_path / "person.png"
    garment = tmp_path / "garment.png"
    mask = tmp_path / "mask.png"
    Image.new("RGB", (8, 8), "white").save(person)
    Image.new("RGB", (8, 8), "red").save(garment)
    Image.new("L", (8, 8), "white").save(mask)

    result = VPEngine(
        output_dir=tmp_path / "out",
        image_size=8,
        lora_loader=BrandLoRALoader(registry),
    ).render(TryOnRequest(person_image=person, garment_image=garment, mask_image=mask, brand_id="demo-brand"))

    assert result.metadata["brand_id"] == "demo-brand"
    assert result.metadata["lora_rank"] == 8
