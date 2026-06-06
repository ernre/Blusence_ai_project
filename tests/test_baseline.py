from pathlib import Path

import httpx
import pytest
from PIL import Image

from vpe.baseline import FashnBaselineVTON, FashnConfig, StubBaselineVTON
from vpe.types import TryOnRequest


def _write_image(path: Path, color: str) -> Path:
    Image.new("RGB", (8, 8), color).save(path)
    return path


def _write_mask(path: Path) -> Path:
    Image.new("L", (8, 8), 255).save(path)
    return path


def test_stub_baseline_renders(tmp_path: Path) -> None:
    person = _write_image(tmp_path / "person.png", "white")
    garment = _write_image(tmp_path / "garment.png", "blue")
    mask = _write_mask(tmp_path / "mask.png")

    result = StubBaselineVTON(output_dir=tmp_path, image_size=8).render(
        TryOnRequest(person_image=person, garment_image=garment, mask_image=mask)
    )

    assert result.image_path.exists()
    assert result.engine == "stub-baseline"


def test_fashn_requires_api_key() -> None:
    with pytest.raises(ValueError, match="FASHN_API_KEY"):
        FashnBaselineVTON(FashnConfig(api_url="https://example.test", api_key=""))


def test_fashn_adapter_submits_and_downloads(tmp_path: Path) -> None:
    person = _write_image(tmp_path / "person.png", "white")
    garment = _write_image(tmp_path / "garment.png", "blue")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(200, json={"id": "job-1"})
        if request.url.path.endswith("/job-1"):
            return httpx.Response(200, json={"status": "succeeded", "output_url": "https://api.test/out.png"})
        return httpx.Response(200, content=b"fake-png")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = FashnBaselineVTON(
        FashnConfig(api_url="https://api.test", api_key="secret", poll_interval_seconds=0),
        client=client,
    )

    result = adapter.render(TryOnRequest(person_image=person, garment_image=garment))

    assert result.image_path.exists()
    assert result.metadata["provider_job_id"] == "job-1"
