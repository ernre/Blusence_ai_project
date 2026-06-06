"""IDM-VTON research provider scaffold.

IDM-VTON is useful as an open-source research baseline, but the upstream code
and checkpoints are published under CC BY-NC-SA 4.0. Keep it separate from
proprietary VPE model ownership unless a commercial license is obtained.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from vpe.providers.base import ProviderDescriptor, ProviderUnavailableError, TryOnProvider
from vpe.types import TryOnRequest, TryOnResult


@dataclass(frozen=True)
class IDMVTONConfig:
    """Runtime settings for a local IDM-VTON research checkout."""

    repo_path: Path | None
    model_dir: Path | None
    device: str = "cuda"
    non_commercial_acknowledged: bool = False

    @classmethod
    def from_env(cls) -> "IDMVTONConfig":
        repo_path = os.getenv("IDM_VTON_REPO_PATH", "").strip()
        model_dir = os.getenv("IDM_VTON_MODEL_DIR", "").strip()
        return cls(
            repo_path=Path(repo_path) if repo_path else None,
            model_dir=Path(model_dir) if model_dir else None,
            device=os.getenv("IDM_VTON_DEVICE", "cuda"),
            non_commercial_acknowledged=(
                os.getenv("IDM_VTON_NON_COMMERCIAL_ACK", "false").lower() == "true"
            ),
        )


class IDMVTONResearchProvider(TryOnProvider):
    """Registered provider path for the self-hosted IDM-VTON research baseline."""

    descriptor = ProviderDescriptor(
        id="idm_vton",
        label="IDM-VTON research baseline",
        role="open-source-research",
        status="scaffolded",
        requires=(
            "IDM_VTON_REPO_PATH",
            "IDM_VTON_MODEL_DIR",
            "IDM_VTON_NON_COMMERCIAL_ACK=true",
            "CUDA GPU",
        ),
        notes=(
            "Use only as a research baseline unless licensing is resolved. "
            "The production VPE engine should reimplement or replace this path."
        ),
    )

    def __init__(self, config: IDMVTONConfig) -> None:
        self._config = config

    def render(self, request: TryOnRequest) -> TryOnResult:
        self._validate_setup()
        raise ProviderUnavailableError(
            "IDM-VTON provider is registered as the self-hosted research path, "
            "but the external inference runner is not wired into this monorepo yet. "
            "Use docs/IDM_VTON_PROVIDER.md before enabling it for live jobs."
        )

    def _validate_setup(self) -> None:
        if not self._config.non_commercial_acknowledged:
            raise ProviderUnavailableError(
                "Set IDM_VTON_NON_COMMERCIAL_ACK=true only after confirming the "
                "CC BY-NC-SA 4.0 research-license boundary."
            )
        if self._config.repo_path is None or not self._config.repo_path.exists():
            raise ProviderUnavailableError("IDM_VTON_REPO_PATH must point to an IDM-VTON checkout.")
        if self._config.model_dir is None or not self._config.model_dir.exists():
            raise ProviderUnavailableError("IDM_VTON_MODEL_DIR must point to downloaded IDM-VTON weights.")


__all__ = ["IDMVTONConfig", "IDMVTONResearchProvider"]
