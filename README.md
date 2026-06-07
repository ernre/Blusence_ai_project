# VPE-1.0: VTON-Prime Engine

VPE-1.0 is a provider-oriented virtual try-on monorepo. It keeps the product
surface stable while different generation backends can be selected for local
preview, external benchmarking, or self-hosted research.

The current implementation is production-shaped and CPU-runnable: heavyweight
diffusion, pose, PEFT, and TensorRT paths are isolated behind explicit providers
and optional dependencies so the repository can test end-to-end without
committing proprietary weights.

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

- `vpe.providers`: Product provider registry for local, FASHN.ai, and IDM-VTON paths.
- `vpe.baseline`: Compatibility package for original benchmark adapter tests.
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
- Phase 10: Provider registry for product preview, FASHN benchmark, and IDM-VTON research paths.

## Boundaries

- No model weights, provider credentials, or generated production artifacts are
  committed.
- FASHN.ai is an external benchmark provider, not proprietary model IP.
- IDM-VTON is an open-source research provider path. Its upstream license is
  CC BY-NC-SA 4.0, so keep it separate from commercial/proprietary claims unless
  licensing is resolved. See `docs/IDM_VTON_PROVIDER.md`.
- Real SDXL/Diffusers, DensePose/DWPose, PEFT, and TensorRT integrations should
  implement the interfaces already present in `src/vpe/core`.

## Provider Strategy

The backend selects the active try-on provider with `VPE_TRYON_PROVIDER`:

```text
local    product preview and smoke tests
fashn    FASHN.ai external benchmark / launch accelerator
idm_vton IDM-VTON hosted Hugging Face Space research baseline
```

Inspect the registry while the backend is running:

```powershell
Invoke-RestMethod http://localhost:8000/v1/providers
```

The frontend Health page also displays the active provider.

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

## IDM-VTON Research Path

IDM-VTON is registered as `VPE_TRYON_PROVIDER=idm_vton` so the project can run a
real research VTON model without changing the frontend/backend contract. The
current provider calls the hosted Hugging Face Space at `yisol/IDM-VTON`.
Set `IDM_VTON_NON_COMMERCIAL_ACK=true` after reviewing the license boundary, and
set `IDM_VTON_HF_TOKEN` or `HF_TOKEN` when public ZeroGPU quota is exhausted.

See `docs/IDM_VTON_PROVIDER.md` for the implementation plan.

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

## Real Garment Catalog

The app no longer ships fake sample garments. To show real catalog images:

1. Add product photos you own or have permission to use under `data/catalog/images`.
2. Add rows to `data/catalog/garments.csv`.
3. Run the backend and open the Studio. The catalog grid reads `GET /v1/catalog/garments`.

CSV format:

```csv
id,name,brand,category,image_path,image_url,source_url,license
blue-jacket,Blue Jacket,Acme,outerwear,images/blue-jacket.jpg,,https://example.com/products/blue-jacket,owned
```

Use `image_path` for local catalog files or `image_url` for public product images.
The local preview provider still produces a placeholder try-on. Real generation
requires either `VPE_TRYON_PROVIDER=fashn` plus a valid `FASHN_API_KEY`, or
`VPE_TRYON_PROVIDER=idm_vton` plus Hugging Face Space quota.
