from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

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
