# Serving

FastAPI, queueing, and GPU worker code for VPE product inference.

The API keeps a stable upload/run/status contract while the active generation
backend is selected by `VPE_TRYON_PROVIDER`:

- `local`: deterministic product preview.
- `fashn`: FASHN.ai external benchmark.
- `idm_vton`: IDM-VTON research provider path.

Use `GET /v1/providers` to inspect the configured provider strategy.
