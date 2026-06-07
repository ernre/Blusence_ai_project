"""FastAPI serving surface."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel

from vpe.providers import (
    TryOnProvider,
    active_provider_id,
    build_tryon_provider,
    provider_descriptors,
)
from vpe.types import TryOnRequest, TryOnResult


class JobResponse(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    status: str
    images: list[str] | None = None
    source_images: list[str] | None = None
    latency_ms: int | None = None
    error: str | None = None


class JobSummary(BaseModel):
    id: str
    status: str
    thumbnail_url: str
    latency_ms: int | None
    created_at: str


class JobsResponse(BaseModel):
    jobs: list[JobSummary]


class CatalogGarment(BaseModel):
    id: str
    name: str
    brand: str | None = None
    category: str
    image_url: str
    source_url: str | None = None
    license: str | None = None


class CatalogResponse(BaseModel):
    garments: list[CatalogGarment]


class ProviderSummary(BaseModel):
    id: str
    label: str
    role: str
    status: str
    requires: list[str]
    notes: str
    active: bool


class ProvidersResponse(BaseModel):
    active_provider: str
    providers: list[ProviderSummary]


app = FastAPI(title="VPE-1.0 Serving API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

serving_root = Path("outputs/serving")
upload_root = serving_root / "uploads"
result_root = serving_root / "results"
catalog_root = Path("data/catalog")
catalog_images_root = catalog_root / "images"
catalog_manifest = catalog_root / "garments.csv"
upload_root.mkdir(parents=True, exist_ok=True)
result_root.mkdir(parents=True, exist_ok=True)
catalog_images_root.mkdir(parents=True, exist_ok=True)
app.mount("/artifacts", StaticFiles(directory=serving_root), name="artifacts")
app.mount("/catalog-assets", StaticFiles(directory=catalog_images_root), name="catalog-assets")

provider_cache: dict[str, TryOnProvider] = {}
jobs: dict[str, JobStatus] = {}
job_summaries: dict[str, JobSummary] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "VPE-1.0", "provider": active_provider_id()}


@app.get("/healthz")
def healthz() -> dict[str, bool]:
    return {"ok": True}


@app.get("/metrics")
def metrics() -> dict[str, int]:
    statuses = [payload.status for payload in jobs.values()]
    return {
        "jobs_total": len(statuses),
        "jobs_succeeded": statuses.count("done"),
        "jobs_failed": statuses.count("error"),
    }


@app.post("/v1/tryon", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_tryon(
    background_tasks: BackgroundTasks,
    request: Request,
    person: list[UploadFile] = File(...),
    garment: UploadFile = File(...),
    category: str = Form(...),
    brand_id: str | None = Form(default=None),
    steps: int | None = Form(default=None),
) -> JobResponse:
    if not person:
        raise HTTPException(status_code=422, detail="At least one person image is required")
    if steps is not None and not 4 <= steps <= 8:
        raise HTTPException(status_code=422, detail="steps must be between 4 and 8")

    job_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    jobs[job_id] = JobStatus(status="queued")
    job_summaries[job_id] = JobSummary(
        id=job_id,
        status="queued",
        thumbnail_url="",
        latency_ms=None,
        created_at=created_at,
    )

    person_paths = [await _persist_upload(upload, job_id, f"person-{index}") for index, upload in enumerate(person)]
    garment_path = await _persist_upload(garment, job_id, "garment")
    mask_path = _create_full_mask(person_paths[0], job_id)
    source_urls = [_artifact_url(request, path) for path in person_paths]
    jobs[job_id] = JobStatus(status="queued", source_images=source_urls)
    background_tasks.add_task(
        _process_tryon_job,
        job_id,
        created_at,
        str(request.base_url).rstrip("/"),
        person_paths,
        garment_path,
        mask_path,
        source_urls,
        category,
        brand_id,
    )
    return JobResponse(job_id=job_id)


@app.get("/v1/tryon/{job_id}", response_model=JobStatus)
def get_tryon_job(job_id: str) -> JobStatus:
    payload = jobs.get(job_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return payload


@app.get("/v1/jobs", response_model=JobsResponse)
def list_jobs() -> JobsResponse:
    sorted_jobs = sorted(job_summaries.values(), key=lambda job: job.created_at, reverse=True)
    return JobsResponse(jobs=sorted_jobs)


@app.get("/v1/catalog/garments", response_model=CatalogResponse)
def list_catalog_garments(request: Request, category: str | None = None) -> CatalogResponse:
    garments = _load_catalog(request)
    if category:
        garments = [garment for garment in garments if garment.category == category]
    return CatalogResponse(garments=garments)


@app.get("/v1/providers", response_model=ProvidersResponse)
def list_tryon_providers() -> ProvidersResponse:
    active = active_provider_id()
    return ProvidersResponse(
        active_provider=active,
        providers=[
            ProviderSummary(
                id=descriptor.id,
                label=descriptor.label,
                role=descriptor.role,
                status=descriptor.status,
                requires=list(descriptor.requires),
                notes=descriptor.notes,
                active=descriptor.id == active,
            )
            for descriptor in provider_descriptors()
        ],
    )


def _render_tryon(request: TryOnRequest) -> TryOnResult:
    return _active_provider().render(request)


def _process_tryon_job(
    job_id: str,
    created_at: str,
    base_url: str,
    person_paths: list[Path],
    garment_path: Path,
    mask_path: Path,
    source_urls: list[str],
    category: str,
    brand_id: str | None,
) -> None:
    jobs[job_id] = JobStatus(status="running", source_images=source_urls)
    job_summaries[job_id].status = "running"
    try:
        started = perf_counter()
        result = _render_tryon(
            TryOnRequest(
                person_image=person_paths[0],
                garment_image=garment_path,
                mask_image=mask_path,
                person_views=tuple(person_paths[1:]),
                category=category,
                brand_id=brand_id,
            )
        )
        latency_ms = int((perf_counter() - started) * 1000)
        output_path = result_root / f"{job_id}{result.image_path.suffix or '.png'}"
        result.image_path.replace(output_path)
        image_url = _artifact_url_from_base(base_url, output_path)
        jobs[job_id] = JobStatus(
            status="done",
            images=[image_url],
            source_images=source_urls,
            latency_ms=latency_ms,
        )
        job_summaries[job_id] = JobSummary(
            id=job_id,
            status="done",
            thumbnail_url=image_url,
            latency_ms=latency_ms,
            created_at=created_at,
        )
    except Exception as exc:
        jobs[job_id] = JobStatus(status="error", source_images=source_urls, error=str(exc))
        job_summaries[job_id].status = "error"
        job_summaries[job_id].thumbnail_url = source_urls[0] if source_urls else ""


def _active_provider() -> TryOnProvider:
    provider_id = active_provider_id()
    if provider_id not in provider_cache:
        provider_cache[provider_id] = build_tryon_provider(
            provider_id=provider_id,
            output_dir=result_root,
            image_size=256,
        )
    return provider_cache[provider_id]


async def _persist_upload(upload: UploadFile, job_id: str, stem: str) -> Path:
    if upload.content_type is not None and not upload.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail=f"{upload.filename} is not an image")
    suffix = Path(upload.filename or "upload.png").suffix or ".png"
    job_dir = upload_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    path = job_dir / f"{stem}{suffix}"
    path.write_bytes(await upload.read())
    return path


def _create_full_mask(person_image: Path, job_id: str) -> Path:
    with Image.open(person_image) as image:
        mask = Image.new("L", image.size, 255)
    mask_path = upload_root / job_id / "mask.png"
    mask.save(mask_path)
    return mask_path


def _artifact_url(request: Request, path: Path) -> str:
    return _artifact_url_from_base(str(request.base_url).rstrip("/"), path)


def _artifact_url_from_base(base_url: str, path: Path) -> str:
    relative = path.relative_to(serving_root).as_posix()
    return f"{base_url}/artifacts/{relative}"


def _load_catalog(request: Request) -> list[CatalogGarment]:
    if not catalog_manifest.exists():
        return []
    garments: list[CatalogGarment] = []
    with catalog_manifest.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            garment = _catalog_row_to_garment(request, row)
            if garment is not None:
                garments.append(garment)
    return garments


def _catalog_row_to_garment(request: Request, row: dict[str, str]) -> CatalogGarment | None:
    garment_id = row.get("id", "").strip()
    name = row.get("name", "").strip()
    category = row.get("category", "").strip()
    image_path = row.get("image_path", "").strip()
    image_url = row.get("image_url", "").strip()
    if not garment_id or not name or not category:
        return None
    resolved_image_url = image_url
    if image_path:
        local_path = (catalog_root / image_path).resolve()
        try:
            local_path.relative_to(catalog_images_root.resolve())
        except ValueError:
            return None
        if not local_path.exists():
            return None
        relative = local_path.relative_to(catalog_images_root.resolve()).as_posix()
        resolved_image_url = str(request.base_url).rstrip("/") + f"/catalog-assets/{relative}"
    if not resolved_image_url:
        return None
    return CatalogGarment(
        id=garment_id,
        name=name,
        brand=row.get("brand", "").strip() or None,
        category=category,
        image_url=resolved_image_url,
        source_url=row.get("source_url", "").strip() or None,
        license=row.get("license", "").strip() or None,
    )
