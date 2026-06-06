"""Inference worker."""

from __future__ import annotations

from vpe.core import VPEngine
from vpe.serving.queue import InferenceJob, JobStore


def process_job(job: InferenceJob, store: JobStore, engine: VPEngine | None = None) -> None:
    """Process one queued inference job."""

    selected_engine = engine or VPEngine()
    store.set_status(job.job_id, "running")
    try:
        result = selected_engine.render(job.request)
    except Exception:
        store.set_status(job.job_id, "failed")
        raise
    store.set_status(job.job_id, "succeeded", result.image_path)


def main() -> None:
    """Placeholder worker entry point for Docker local stack."""

    print("VPE worker is ready. Configure Redis/RQ for production queue consumption.")


if __name__ == "__main__":
    main()
