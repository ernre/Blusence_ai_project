# IDM-VTON Provider Plan

## Purpose

IDM-VTON is the right open-source reference point for the next technical phase:
real diffusion-based virtual try-on using person images, garment images, masks,
pose conditioning, and garment feature injection. In this project it should be
treated as a research/self-hosted provider, not as proprietary VPE IP.

## Boundary

Use IDM-VTON to:

- validate the end-to-end real-image workflow;
- benchmark realism, garment fidelity, and pose robustness;
- learn which model components belong in the proprietary VPE engine.

Do not use IDM-VTON to:

- claim proprietary ownership of upstream code/checkpoints;
- ship commercial output without licensing review;
- train proprietary models on third-party outputs or datasets without rights.

The upstream project and checkpoints are CC BY-NC-SA 4.0. Keep the checkout and
weights outside this repository unless a commercial license is obtained.

## Provider Contract

The monorepo now exposes three provider roles:

```text
local    -> product preview and smoke tests
fashn    -> external paid benchmark / launch accelerator
idm_vton -> open-source research baseline / self-hosted model path
```

The serving API keeps the same product contract:

```text
POST /v1/tryon
GET  /v1/tryon/{job_id}
GET  /v1/providers
```

That lets the frontend and catalog flow stay stable while generation backends
change behind the provider registry.

## Setup Target

The future runnable IDM-VTON adapter should:

1. Load IDM-VTON once per worker process.
2. Accept the existing `TryOnRequest`.
3. Run human parsing, OpenPose, DensePose, and mask preparation.
4. Execute IDM-VTON inference with the uploaded person and garment images.
5. Write the result into `outputs/serving/results`.
6. Return a normal `TryOnResult` with provider metadata.

## Environment

```powershell
$env:VPE_TRYON_PROVIDER="idm_vton"
$env:IDM_VTON_REPO_PATH="C:\path\to\IDM-VTON"
$env:IDM_VTON_MODEL_DIR="C:\path\to\idm-vton-weights"
$env:IDM_VTON_DEVICE="cuda"
$env:IDM_VTON_NON_COMMERCIAL_ACK="true"
```

`IDM_VTON_NON_COMMERCIAL_ACK=true` is intentionally explicit. It should only be
set after the license boundary is understood.

## Next Implementation Step

Create an external runner wrapper instead of copying the upstream repository
into this project. The safest path is:

- keep IDM-VTON in a separate checkout;
- create a small Python runner that imports its inference pipeline;
- call that runner from `IDMVTONResearchProvider`;
- add GPU-only integration tests that are skipped when CUDA/checkpoints are not
  available.
