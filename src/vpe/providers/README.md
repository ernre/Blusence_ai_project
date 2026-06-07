# Providers

The provider layer is the product boundary for try-on generation.

- `local`: CPU-runnable preview provider for frontend/backend workflow testing.
- `fashn`: paid external benchmark provider using the documented FASHN.ai API.
- `idm_vton`: hosted IDM-VTON Hugging Face Space research baseline.

Serving code should select providers through `VPE_TRYON_PROVIDER` and the
registry in `vpe.providers.registry`. Training code should not call external
providers directly.
