from pathlib import Path
from typing import Any

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
        IDMVTONConfig(output_dir=tmp_path, non_commercial_acknowledged=False)
    )

    with pytest.raises(ProviderUnavailableError, match="CC BY-NC-SA"):
        provider.render(TryOnRequest(person_image=person, garment_image=garment))


class _FakeIDMVTONJob:
    def __init__(self, output: Path) -> None:
        self._output = output

    def result(self, timeout: float | None = None) -> tuple[str, str]:
        return (str(self._output), str(self._output))


class _FakeIDMVTONClient:
    def __init__(self, output: Path) -> None:
        self.output = output
        self.calls: list[tuple[tuple[Any, ...], str]] = []

    def submit(self, *args: object, api_name: str) -> _FakeIDMVTONJob:
        self.calls.append((args, api_name))
        return _FakeIDMVTONJob(self.output)


def test_idm_vton_provider_submits_space_payload_and_copies_output(tmp_path: Path) -> None:
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")
    hosted_output = _image(tmp_path / "hosted-output.png", "blue")
    client = _FakeIDMVTONClient(hosted_output)
    provider = IDMVTONResearchProvider(
        IDMVTONConfig(
            output_dir=tmp_path / "results",
            non_commercial_acknowledged=True,
            garment_description="red shirt",
            denoise_steps=20,
            seed=123,
            timeout_seconds=1,
        ),
        client=client,
    )

    result = provider.render(TryOnRequest(person_image=person, garment_image=garment, category="tops"))

    assert result.image_path.exists()
    assert result.image_path.parent == tmp_path / "results"
    assert result.metadata["provider_id"] == "idm_vton"
    assert result.metadata["space_id"] == "yisol/IDM-VTON"
    args, api_name = client.calls[0]
    assert api_name == "/tryon"
    assert args[0]["background"]["orig_name"] == "person.png"
    assert args[1]["orig_name"] == "garment.png"
    assert args[2] == "red shirt"
    assert args[3] is True
    assert args[4] is False
    assert args[5] == 20
    assert args[6] == 123
