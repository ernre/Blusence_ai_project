"""FastAPI serving surface."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from vpe.core import VPEngine
from vpe.serving.queue import JobStore, MemoryInferenceQueue
from vpe.serving.worker import process_job
from vpe.types import TryOnRequest


class JobResponse(BaseModel):
    job_id: str
    status: str


class JobStatus(BaseModel):
    status: str
    output_path: str | None = None


app = FastAPI(title="VPE-1.0 Serving API", version="0.1.0")
store = JobStore()
queue = MemoryInferenceQueue(store)
engine = VPEngine(output_dir=Path("outputs/serving"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "VPE-1.0"}


@app.get("/metrics")
def metrics() -> dict[str, int]:
    statuses = [payload["status"] for payload in store.statuses.values()]
    return {
        "jobs_total": len(statuses),
        "jobs_succeeded": statuses.count("succeeded"),
        "jobs_failed": statuses.count("failed"),
    }


@app.post("/v1/tryon", response_model=JobResponse)
async def create_tryon(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    mask_image: UploadFile = File(...),
) -> JobResponse:
    person_path = await _persist_upload(person_image)
    garment_path = await _persist_upload(garment_image)
    mask_path = await _persist_upload(mask_image)
    job_id = queue.enqueue(
        TryOnRequest(person_image=person_path, garment_image=garment_path, mask_image=mask_path)
    )
    process_job(queue.get(), store, engine)
    return JobResponse(job_id=job_id, status=store.statuses[job_id]["status"])


@app.get("/v1/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    payload = store.statuses.get(job_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**payload)


async def _persist_upload(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "upload.png").suffix or ".png"
    with NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(await upload.read())
        return Path(handle.name)
