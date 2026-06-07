"""IDM-VTON research provider.

IDM-VTON is useful as an open-source research baseline, but the upstream code
and checkpoints are published under CC BY-NC-SA 4.0. Keep it separate from
proprietary VPE model ownership unless a commercial license is obtained.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from vpe.providers.base import ProviderDescriptor, ProviderUnavailableError, TryOnProvider
from vpe.types import TryOnRequest, TryOnResult


class IDMVTONClient(Protocol):
    """Minimal client surface used from `gradio_client.Client`."""

    def submit(self, *args: object, api_name: str) -> Any:
        """Submit a queued Gradio job."""


class IDMVTONJob(Protocol):
    """Minimal queued job surface returned by `gradio_client.Client.submit`."""

    def result(self, timeout: float | None = None) -> Any:
        """Wait for and return the hosted inference result."""


@dataclass(frozen=True)
class IDMVTONConfig:
    """Runtime settings for the hosted IDM-VTON research provider."""

    output_dir: Path
    space_id: str = "yisol/IDM-VTON"
    api_name: str = "/tryon"
    hf_token: str = ""
    garment_description: str = ""
    auto_mask: bool = True
    auto_crop: bool = False
    denoise_steps: int = 20
    seed: int = 42
    timeout_seconds: float = 600.0
    non_commercial_acknowledged: bool = False

    @classmethod
    def from_env(cls, output_dir: Path = Path("outputs/idm_vton")) -> "IDMVTONConfig":
        """Create IDM-VTON settings from environment variables."""

        token = (
            os.getenv("IDM_VTON_HF_TOKEN", "").strip()
            or os.getenv("HF_TOKEN", "").strip()
            or os.getenv("HUGGINGFACE_TOKEN", "").strip()
        )
        return cls(
            output_dir=output_dir,
            space_id=os.getenv("IDM_VTON_SPACE_ID", "yisol/IDM-VTON"),
            api_name=os.getenv("IDM_VTON_API_NAME", "/tryon"),
            hf_token=token,
            garment_description=os.getenv("IDM_VTON_GARMENT_DESCRIPTION", ""),
            auto_mask=os.getenv("IDM_VTON_AUTO_MASK", "true").lower() == "true",
            auto_crop=os.getenv("IDM_VTON_AUTO_CROP", "false").lower() == "true",
            denoise_steps=int(os.getenv("IDM_VTON_DENOISE_STEPS", "20")),
            seed=int(os.getenv("IDM_VTON_SEED", "42")),
            timeout_seconds=float(os.getenv("IDM_VTON_TIMEOUT_SECONDS", "600")),
            non_commercial_acknowledged=(
                os.getenv("IDM_VTON_NON_COMMERCIAL_ACK", "false").lower() == "true"
            ),
        )


class IDMVTONResearchProvider(TryOnProvider):
    """Hosted Hugging Face Space provider for the IDM-VTON research baseline."""

    descriptor = ProviderDescriptor(
        id="idm_vton",
        label="IDM-VTON Hugging Face Space",
        role="open-source-research",
        status="hosted",
        requires=(
            "IDM_VTON_NON_COMMERCIAL_ACK=true",
            "HF_TOKEN recommended for ZeroGPU quota",
        ),
        notes=(
            "Calls the yisol/IDM-VTON Hugging Face Space as a research baseline. "
            "Use a Hugging Face token when public ZeroGPU quota is exhausted."
        ),
    )

    def __init__(self, config: IDMVTONConfig, client: IDMVTONClient | None = None) -> None:
        self._config = config
        self._client = client

    def render(self, request: TryOnRequest) -> TryOnResult:
        self._validate_setup()
        self._validate_request(request)
        self._config.output_dir.mkdir(parents=True, exist_ok=True)
        result = self._submit_request(request)
        output_path = self._copy_result_image(result)
        return TryOnResult(
            image_path=output_path,
            engine=f"idm-vton-space-{self._config.space_id}",
            metadata={
                "provider_id": self.descriptor.id,
                "provider_role": self.descriptor.role,
                "space_id": self._config.space_id,
                "api_name": self._config.api_name,
                "auto_mask": self._config.auto_mask,
                "auto_crop": self._config.auto_crop,
                "denoise_steps": self._config.denoise_steps,
                "seed": request.seed if request.seed is not None else self._config.seed,
            },
        )

    def _validate_setup(self) -> None:
        if not self._config.non_commercial_acknowledged:
            raise ProviderUnavailableError(
                "Set IDM_VTON_NON_COMMERCIAL_ACK=true only after confirming the "
                "CC BY-NC-SA 4.0 research-license boundary."
            )

    @staticmethod
    def _validate_request(request: TryOnRequest) -> None:
        if not request.person_image.exists():
            raise FileNotFoundError(f"Person image does not exist: {request.person_image}")
        if not request.garment_image.exists():
            raise FileNotFoundError(f"Garment image does not exist: {request.garment_image}")

    def _submit_request(self, request: TryOnRequest) -> Any:
        client = self._client or self._build_client()
        person_payload = {
            "background": self._as_gradio_file(request.person_image),
            "layers": [],
            "composite": None,
        }
        job = client.submit(
            person_payload,
            self._as_gradio_file(request.garment_image),
            self._garment_description(request),
            self._config.auto_mask,
            self._config.auto_crop,
            self._config.denoise_steps,
            request.seed if request.seed is not None else self._config.seed,
            api_name=self._config.api_name,
        )
        try:
            return job.result(timeout=self._config.timeout_seconds)
        except Exception as exc:
            raise ProviderUnavailableError(
                "IDM-VTON Hugging Face Space inference failed. If the error mentions "
                "ZeroGPU quota, set HF_TOKEN or IDM_VTON_HF_TOKEN with an account that "
                "has available quota."
            ) from exc

    def _build_client(self) -> IDMVTONClient:
        try:
            from gradio_client import Client
        except ImportError as exc:
            raise ProviderUnavailableError(
                "Install gradio-client to use VPE_TRYON_PROVIDER=idm_vton."
            ) from exc

        # Older gradio-client versions print a Unicode checkmark during init,
        # which can crash cp1254 Windows consoles. Keep provider startup quiet.
        with contextlib.redirect_stdout(io.StringIO()):
            return Client(
                self._config.space_id,
                hf_token=self._config.hf_token or None,
                output_dir=self._config.output_dir,
                verbose=False,
            )

    @staticmethod
    def _as_gradio_file(path: Path) -> dict[str, object]:
        try:
            from gradio_client import file
        except ImportError as exc:
            raise ProviderUnavailableError(
                "Install gradio-client to use VPE_TRYON_PROVIDER=idm_vton."
            ) from exc
        return file(path)

    def _garment_description(self, request: TryOnRequest) -> str:
        if self._config.garment_description:
            return self._config.garment_description
        category = (request.category or "garment").replace("-", " ")
        return f"{category} clothing"

    def _copy_result_image(self, result: Any) -> Path:
        output = result[0] if isinstance(result, (tuple, list)) else result
        source = self._extract_output_path(output)
        suffix = source.suffix or ".png"
        destination = self._config.output_dir / f"idm-vton-output{suffix}"
        shutil.copyfile(source, destination)
        return destination

    @staticmethod
    def _extract_output_path(output: Any) -> Path:
        if isinstance(output, (str, Path)):
            path = Path(output)
        elif isinstance(output, dict) and isinstance(output.get("path"), str):
            path = Path(output["path"])
        else:
            raise ProviderUnavailableError("IDM-VTON Space returned an unexpected output payload.")
        if not path.exists():
            raise ProviderUnavailableError(f"IDM-VTON output file does not exist: {path}")
        return path


__all__ = ["IDMVTONConfig", "IDMVTONResearchProvider"]
