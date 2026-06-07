# IDM-VTON Provider Plan

## Purpose

IDM-VTON is the right open-source reference point for the next technical phase:
real diffusion-based virtual try-on using person images, garment images, masks,
pose conditioning, and garment feature injection. In this project it is wired as
a hosted Hugging Face Space provider and should be treated as research baseline,
not proprietary VPE IP.

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
idm_vton -> open-source research baseline / hosted Hugging Face Space path
```

The serving API keeps the same product contract:

```text
POST /v1/tryon
GET  /v1/tryon/{job_id}
GET  /v1/providers
```

That lets the frontend and catalog flow stay stable while generation backends
change behind the provider registry.

## Current Hosted Setup

The current adapter calls the public Space:

```text
https://huggingface.co/spaces/yisol/IDM-VTON
```

The Space exposes:

```text
predict(dict, garm_img, garment_des, is_checked, is_checked_crop, denoise_steps, seed, api_name="/tryon")
```

The provider accepts the existing `TryOnRequest`, sends the person and garment
images to the Space, copies the returned image into `outputs/serving/results`,
and returns a normal `TryOnResult`.

## Environment

```powershell
$env:VPE_TRYON_PROVIDER="idm_vton"
$env:IDM_VTON_NON_COMMERCIAL_ACK="true"
$env:IDM_VTON_SPACE_ID="yisol/IDM-VTON"
$env:IDM_VTON_HF_TOKEN="hf_..." # optional, but recommended for ZeroGPU quota
$env:IDM_VTON_DENOISE_STEPS="20"
```

`IDM_VTON_NON_COMMERCIAL_ACK=true` is intentionally explicit. It should only be
set after the license boundary is understood.

If Hugging Face returns a ZeroGPU quota error, create a token at
`https://huggingface.co/settings/tokens` and set `IDM_VTON_HF_TOKEN`,
`HF_TOKEN`, or `HUGGINGFACE_TOKEN`.

## Future Self-Hosted Step

For production control, create a self-hosted runner instead of depending on the
public Space:

- keep IDM-VTON in a separate checkout;
- create a small Python runner that imports its inference pipeline;
- call that runner from `IDMVTONResearchProvider`;
- add GPU-only integration tests that are skipped when CUDA/checkpoints are not
  available.
