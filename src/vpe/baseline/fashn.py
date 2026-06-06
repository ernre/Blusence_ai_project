"""Fashn.ai VTON-1.5 baseline adapter.

The adapter is intentionally isolated from model training code. It is suitable
for evaluation references and benchmark comparisons only.
"""

from __future__ import annotations

import base64
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from vpe.baseline.base import BaselineVTON
from vpe.types import TryOnRequest, TryOnResult


class BaselineProviderError(RuntimeError):
    """Raised when the external baseline provider returns an invalid response."""


@dataclass(frozen=True)
class FashnConfig:
    """Connection settings for the Fashn.ai adapter."""

    api_url: str
    api_key: str
    timeout_seconds: float = 60.0
    poll_interval_seconds: float = 1.0


class FashnBaselineVTON(BaselineVTON):
    """HTTP adapter for Fashn.ai VTON-1.5 benchmark calls."""

    def __init__(self, config: FashnConfig, client: httpx.Client | None = None) -> None:
        if not config.api_key:
            raise ValueError("FASHN_API_KEY is required for FashnBaselineVTON")
        self._config = config
        self._client = client or httpx.Client(timeout=config.timeout_seconds)

    def render(self, request: TryOnRequest) -> TryOnResult:
        """Submit a try-on job and download the resulting image."""

        self._validate_request(request)
        payload = {
            "model": "vton-1.5",
            "person_image": self._encode_file(request.person_image),
            "garment_image": self._encode_file(request.garment_image),
            "mask_image": self._encode_file(request.mask_image) if request.mask_image else None,
            "seed": request.seed,
        }
        response = self._client.post(
            f"{self._config.api_url.rstrip('/')}/v1/tryon",
            headers={"Authorization": f"Bearer {self._config.api_key}"},
            json={key: value for key, value in payload.items() if value is not None},
        )
        response.raise_for_status()
        job = response.json()
        job_id = self._require_string(job, "id")
        output_url = self._poll_until_complete(job_id)
        output_path = Path("outputs/baseline") / f"fashn-{job_id}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image_response = self._client.get(output_url)
        image_response.raise_for_status()
        output_path.write_bytes(image_response.content)
        return TryOnResult(
            image_path=output_path,
            engine="fashn-vton-1.5",
            metadata={"provider_job_id": job_id},
        )

    def _poll_until_complete(self, job_id: str) -> str:
        deadline = time.monotonic() + self._config.timeout_seconds
        while time.monotonic() < deadline:
            response = self._client.get(
                f"{self._config.api_url.rstrip('/')}/v1/tryon/{job_id}",
                headers={"Authorization": f"Bearer {self._config.api_key}"},
            )
            response.raise_for_status()
            payload = response.json()
            status = self._require_string(payload, "status")
            if status == "succeeded":
                return self._require_string(payload, "output_url")
            if status in {"failed", "cancelled"}:
                raise BaselineProviderError(f"Fashn job {job_id} ended with status {status}")
            time.sleep(self._config.poll_interval_seconds)
        raise TimeoutError(f"Fashn job {job_id} did not complete before timeout")

    @staticmethod
    def _encode_file(path: Path | None) -> str | None:
        if path is None:
            return None
        return base64.b64encode(path.read_bytes()).decode("ascii")

    @staticmethod
    def _require_string(payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise BaselineProviderError(f"Fashn response missing string field: {key}")
        return value

    @staticmethod
    def _validate_request(request: TryOnRequest) -> None:
        for path in [request.person_image, request.garment_image]:
            if not path.exists():
                raise FileNotFoundError(f"Baseline input does not exist: {path}")
