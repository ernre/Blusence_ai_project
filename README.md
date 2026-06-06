# VPE-1.0: VTON-Prime Engine

VPE-1.0 is a proprietary virtual try-on monorepo scaffold. It is designed around a
latent-diffusion inpainting engine with baseline benchmarking, training, evaluation,
latency optimization, and a queue-backed serving API.

## Quick Start

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -e ".[dev]"
pytest
```

## Packages

- `vpe.baseline`: Fashn.ai-compatible benchmark adapter.
- `vpe.core`: VTON inference core and model components.
- `vpe.data`: Dataset ingest, cleaning, pose/mask extraction, and versioning.
- `vpe.training`: Config-driven training entry points.
- `vpe.eval`: Automatic metrics and human-eval exports.
- `vpe.latency`: Optimization and benchmark utilities.
- `vpe.serving`: FastAPI API, queue abstraction, and worker.

## Local Services

```powershell
docker compose up --build
```

The local compose stack includes API, Redis, Postgres, and MinIO placeholders.
No proprietary model weights are committed.
