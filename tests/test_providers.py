from pathlib import Path

import pytest
from PIL import Image

from vpe.providers import (
    IDMVTONConfig,
    IDMVTONResearchProvider,
    ProviderUnavailableError,
    active_provider_id,
    build_tryon_provider,
)
from vpe.providers.local import LocalPreviewProvider
from vpe.types import TryOnRequest


def _image(path: Path, color: str, mode: str = "RGB") -> Path:
    Image.new(mode, (8, 8), color).save(path)
    return path


def test_local_provider_renders_product_preview(tmp_path: Path) -> None:
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")
    mask = _image(tmp_path / "mask.png", "white", mode="L")
    provider = build_tryon_provider("local", output_dir=tmp_path, image_size=8)

    result = provider.render(TryOnRequest(person_image=person, garment_image=garment, mask_image=mask))

    assert isinstance(provider, LocalPreviewProvider)
    assert result.image_path.exists()
    assert result.metadata["provider_id"] == "local"
    assert result.metadata["provider_role"] == "product-preview"


def test_provider_aliases_are_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPE_TRYON_PROVIDER", "idm-vton")

    assert active_provider_id() == "idm_vton"


def test_unknown_provider_fails_clearly(tmp_path: Path) -> None:
    with pytest.raises(ProviderUnavailableError, match="Unknown VPE_TRYON_PROVIDER"):
        build_tryon_provider("not-real", output_dir=tmp_path)


def test_idm_vton_requires_license_acknowledgement(tmp_path: Path) -> None:
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")
    provider = IDMVTONResearchProvider(
        IDMVTONConfig(repo_path=tmp_path, model_dir=tmp_path, non_commercial_acknowledged=False)
    )

    with pytest.raises(ProviderUnavailableError, match="CC BY-NC-SA"):
        provider.render(TryOnRequest(person_image=person, garment_image=garment))
