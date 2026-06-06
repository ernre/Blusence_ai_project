# VPE-1.0: VTON-Prime Engine

VPE-1.0 is a proprietary virtual try-on monorepo. It is organized around a
latent-diffusion inpainting engine with baseline benchmarking, training,
evaluation, latency optimization, and a queue-backed serving API.

The current implementation is production-shaped and CPU-runnable: heavyweight
diffusion, pose, PEFT, and TensorRT paths are isolated behind explicit seams and
optional dependencies so the repository can test end-to-end without committing
proprietary weights.

## Python Engine Quick Start

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -e ".[dev]"
pytest
```

If your local `python` is older than 3.11, use a Python 3.11 interpreter for the
editable install. The Docker images use Python 3.11.

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

## Commands

```powershell
$env:PYTHONPATH="src"; python -m pytest
$env:PYTHONPATH="src"; python -m vpe.training.cli --config configs/base.yaml
$env:PYTHONPATH="src"; python -m vpe.latency.benchmark --person-image tests/smoke_dataset/person.png --garment-image tests/smoke_dataset/garment.png --mask-image tests/smoke_dataset/mask.png --image-size 8
uvicorn vpe.serving.api:app --app-dir src --host 0.0.0.0 --port 8000
```

## Phase Deliverables

- Phase 0: Monorepo scaffold, config, Docker, tests, and package READMEs.
- Phase 1: Fashn.ai baseline adapter plus offline baseline stub.
- Phase 2: Inference core with garment encoder and decoupled cross-attention seam.
- Phase 3: Pose conditioning and multi-view consistency seams.
- Phase 4: Dataset manifest, smoke training loop, losses, and checkpoint metadata.
- Phase 5: Brand LoRA registry and inference-time metadata loading.
- Phase 6: Latency plan validation, benchmark CLI, and TensorRT export stub.
- Phase 7: Automatic metrics and human-eval CSV/JSON export.
- Phase 8: FastAPI API, in-memory queue, worker, health, and metrics endpoints.
- Phase 9: Architecture and runbook documentation.

## Boundaries

- No model weights, provider credentials, or generated production artifacts are
  committed.
- The Fashn.ai adapter is benchmark-only. See `LICENSING_NOTES.md`.
- Real SDXL/Diffusers, DensePose/DWPose, PEFT, and TensorRT integrations should
  implement the interfaces already present in `src/vpe/core`.

## FASHN AI Integration

The backend can use FASHN AI as the live try-on provider by setting:

```powershell
$env:VPE_TRYON_PROVIDER="fashn"
$env:FASHN_API_KEY="..."
$env:FASHN_API_URL="https://api.fashn.ai"
$env:FASHN_MODEL_NAME="tryon-v1.6"
```

The adapter follows FASHN's universal API pattern: `POST /v1/run` with
`model_name` and `inputs`, then `GET /v1/status/{id}` until `completed`.
Local uploads are sent as `data:image/...;base64,...` strings, so the browser
does not need to expose public image URLs.

For broader item support such as shoes and accessories, set
`FASHN_MODEL_NAME=tryon-max`; for low-latency clothing try-on, keep the default
`tryon-v1.6`.

## Frontend App

VPE-1.0 also includes a frontend-only Next.js App Router web app for the try-on
experience. It can run fully in mock mode without the Python API.

```powershell
pnpm install
Copy-Item .env.local.example .env.local
pnpm dev
```

Environment variables:

- `NEXT_PUBLIC_USE_MOCK=true`: use the built-in mock job lifecycle.
- `NEXT_PUBLIC_USE_MOCK=false`: call a live backend.
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`: backend base URL for live mode.

Frontend verification commands:

```powershell
pnpm lint
pnpm typecheck
pnpm test
pnpm e2e
pnpm build
```

Frontend Docker build:

```powershell
docker build -f Dockerfile.frontend -t vpe-frontend .
docker run --rm -p 3000:3000 -e NEXT_PUBLIC_USE_MOCK=true vpe-frontend
```
