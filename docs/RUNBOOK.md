# Runbook

## Environment

Target runtime is Python 3.11. Install local dev dependencies:

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -e ".[dev]"
```

## Verify

```powershell
$env:PYTHONPATH="src"
python -m pytest
```

Expected result in the current scaffold: all tests pass. On Python 3.10, use
direct `PYTHONPATH=src` smoke testing if editable install refuses the declared
Python 3.11 target.

## Train Smoke Path

```powershell
$env:PYTHONPATH="src"
python -m vpe.training.cli --config configs/base.yaml --output-dir outputs/training
```

This exercises dataset loading, deterministic seed setup, rendering, losses, and
checkpoint metadata. It does not train proprietary weights.

## Benchmark

```powershell
$env:PYTHONPATH="src"
python -m vpe.latency.benchmark `
  --person-image tests/smoke_dataset/person.png `
  --garment-image tests/smoke_dataset/garment.png `
  --mask-image tests/smoke_dataset/mask.png `
  --image-size 8 `
  --runs 3
```

## Serve Locally

```powershell
$env:PYTHONPATH="src"
uvicorn vpe.serving.api:app --app-dir src --host 0.0.0.0 --port 8000
```

Health endpoint:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Docker

```powershell
docker compose up --build
```

The compose stack starts API, worker placeholder, Redis, Postgres, and MinIO.

## Provider Setup

The serving API selects the active generation path with `VPE_TRYON_PROVIDER`.
The supported values are `local`, `fashn`, and `idm_vton`.

Inspect the provider registry:

```powershell
Invoke-RestMethod http://localhost:8000/v1/providers
```

`local` is the default product preview. It keeps frontend/backend/catalog flows
working without paid APIs or GPU checkpoints.

Set `FASHN_API_KEY` in `.env` before using the FASHN benchmark provider. FASHN
outputs are for benchmarking only and must not be used for training unless
service terms explicitly allow it.

To route frontend live try-on requests through FASHN instead of the local stub:

```powershell
$env:PYTHONPATH="src"
$env:VPE_TRYON_PROVIDER="fashn"
$env:FASHN_API_KEY="..."
$env:FASHN_API_URL="https://api.fashn.ai"
python -m uvicorn vpe.serving.api:app --host 127.0.0.1 --port 8000
```

To run the hosted IDM-VTON research provider:

```powershell
$env:PYTHONPATH="src"
$env:VPE_TRYON_PROVIDER="idm_vton"
$env:IDM_VTON_NON_COMMERCIAL_ACK="true"
$env:IDM_VTON_HF_TOKEN="hf_..." # optional, recommended for ZeroGPU quota
python -m uvicorn vpe.serving.api:app --host 127.0.0.1 --port 8000
```

If Hugging Face returns a ZeroGPU quota error, set a Hugging Face token with
available quota. See `docs/IDM_VTON_PROVIDER.md`.

Keep the frontend in live mode:

```powershell
$env:NEXT_PUBLIC_USE_MOCK="false"
$env:NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
pnpm dev
```

## Production TODOs

- Swap stub image conditioning with Diffusers SDXL/inpainting pipeline.
- Add Redis/RQ or Celery queue implementation behind `MemoryInferenceQueue`.
- Add artifact persistence to MinIO/S3.
- Wire W&B or MLflow tracking in `Trainer`.
- Add GitHub Actions once repository secrets and runner constraints are known.
