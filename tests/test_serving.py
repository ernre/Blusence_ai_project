from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from vpe.serving import api as serving_api
from vpe.serving.api import app
from vpe.serving.queue import JobStore, MemoryInferenceQueue
from vpe.serving.worker import process_job
from vpe.types import TryOnRequest


def _image(path: Path, color: str, mode: str = "RGB") -> Path:
    Image.new(mode, (8, 8), color).save(path)
    return path


def test_memory_worker_processes_job(tmp_path: Path) -> None:
    store = JobStore()
    queue = MemoryInferenceQueue(store)
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")
    mask = _image(tmp_path / "mask.png", "white", mode="L")
    job_id = queue.enqueue(TryOnRequest(person_image=person, garment_image=garment, mask_image=mask))

    process_job(queue.get(), store)

    assert store.statuses[job_id]["status"] == "succeeded"


def test_api_health_and_tryon(tmp_path: Path) -> None:
    client = TestClient(app)
    person = _image(tmp_path / "person.png", "white")
    garment = _image(tmp_path / "garment.png", "red")

    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/healthz").json()["ok"] is True
    with person.open("rb") as person_file, garment.open("rb") as garment_file:
        response = client.post(
            "/v1/tryon",
            files={
                "person": ("person.png", person_file, "image/png"),
                "garment": ("garment.png", garment_file, "image/png"),
            },
            data={"category": "outerwear", "brand_id": "demo-brand", "steps": "6"},
        )

    assert response.status_code == 202
    job_id = response.json()["job_id"]

    job = client.get(f"/v1/tryon/{job_id}").json()
    assert job["status"] == "done"
    assert job["images"][0].startswith("http://testserver/artifacts/")
    assert job["source_images"][0].startswith("http://testserver/artifacts/")

    jobs = client.get("/v1/jobs").json()
    assert jobs["jobs"][0]["id"] == job_id


def test_catalog_endpoint_loads_real_manifest_images(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_root = tmp_path / "catalog"
    images_root = catalog_root / "images"
    images_root.mkdir(parents=True)
    _image(images_root / "jacket.jpg", "blue")
    manifest = catalog_root / "garments.csv"
    manifest.write_text(
        "id,name,brand,category,image_path,image_url,source_url,license\n"
        "jacket-1,Blue Jacket,Acme,outerwear,images/jacket.jpg,,https://example.test/jacket,owned\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(serving_api, "catalog_root", catalog_root)
    monkeypatch.setattr(serving_api, "catalog_images_root", images_root)
    monkeypatch.setattr(serving_api, "catalog_manifest", manifest)

    response = TestClient(app).get("/v1/catalog/garments")

    assert response.status_code == 200
    garment = response.json()["garments"][0]
    assert garment["id"] == "jacket-1"
    assert garment["image_url"].startswith("http://testserver/catalog-assets/")
