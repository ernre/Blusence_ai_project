"""FASHN AI virtual try-on adapter.

The adapter is intentionally isolated from model training code. It is suitable
for evaluation references and benchmark comparisons only.
"""

from __future__ import annotations

import base64
import binascii
import mimetypes
import os
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
    model_name: str = "tryon-v1.6"
    timeout_seconds: float = 120.0
    poll_interval_seconds: float = 3.0
    category: str = "auto"
    mode: str = "balanced"
    garment_photo_type: str = "auto"
    segmentation_free: bool = True
    moderation_level: str = "permissive"
    num_samples: int = 1
    output_format: str = "png"
    return_base64: bool = False

    @classmethod
    def from_env(cls) -> "FashnConfig":
        """Create FASHN settings from environment variables."""

        return cls(
            api_url=os.getenv("FASHN_API_URL", "https://api.fashn.ai"),
            api_key=os.getenv("FASHN_API_KEY", ""),
            model_name=os.getenv("FASHN_MODEL_NAME", "tryon-v1.6"),
            category=os.getenv("FASHN_CATEGORY", "auto"),
            mode=os.getenv("FASHN_MODE", "balanced"),
            garment_photo_type=os.getenv("FASHN_GARMENT_PHOTO_TYPE", "auto"),
            segmentation_free=os.getenv("FASHN_SEGMENTATION_FREE", "true").lower() == "true",
            moderation_level=os.getenv("FASHN_MODERATION_LEVEL", "permissive"),
            num_samples=int(os.getenv("FASHN_NUM_SAMPLES", "1")),
            output_format=os.getenv("FASHN_OUTPUT_FORMAT", "png"),
            return_base64=os.getenv("FASHN_RETURN_BASE64", "false").lower() == "true",
        )


class FashnBaselineVTON(BaselineVTON):
    """HTTP adapter for documented FASHN `/v1/run` and `/v1/status/{id}` calls."""

    def __init__(self, config: FashnConfig, client: httpx.Client | None = None) -> None:
        if not config.api_key:
            raise ValueError("FASHN_API_KEY is required for FashnBaselineVTON")
        self._config = config
        self._client = client or httpx.Client(timeout=config.timeout_seconds)
        self._base_url = self._normalize_base_url(config.api_url)

    def render(self, request: TryOnRequest) -> TryOnResult:
        """Submit a try-on job and download the resulting image."""

        self._validate_request(request)
        payload = {
            "model_name": self._config.model_name,
            "inputs": self._build_inputs(request),
        }
        response = self._client.post(
            f"{self._base_url}/run",
            headers=self._headers(),
            json=payload,
        )
        self._raise_for_api_error(response)
        job = response.json()
        job_id = self._require_string(job, "id")
        outputs, credits_used = self._poll_until_complete(job_id)
        output_path = self._write_output(job_id, outputs[0])
        return TryOnResult(
            image_path=output_path,
            engine=f"fashn-{self._config.model_name}",
            metadata={
                "provider_job_id": job_id,
                "credits_used": credits_used or "",
                "output_count": len(outputs),
            },
        )

    def _poll_until_complete(self, job_id: str) -> tuple[list[str], str | None]:
        deadline = time.monotonic() + self._config.timeout_seconds
        credits_used: str | None = None
        while time.monotonic() < deadline:
            response = self._client.get(
                f"{self._base_url}/status/{job_id}",
                headers=self._headers(),
            )
            self._raise_for_api_error(response)
            credits_used = response.headers.get("x-fashn-credits-used") or credits_used
            payload = response.json()
            status = self._require_string(payload, "status")
            if status == "completed":
                return self._require_output(payload), credits_used
            if status == "failed":
                raise BaselineProviderError(
                    f"FASHN job {job_id} failed: {self._format_error(payload.get('error'))}"
                )
            if status not in {"starting", "in_queue", "processing"}:
                raise BaselineProviderError(f"FASHN job {job_id} returned unknown status {status}")
            time.sleep(self._config.poll_interval_seconds)
        raise TimeoutError(f"FASHN job {job_id} did not complete before timeout")

    def _build_inputs(self, request: TryOnRequest) -> dict[str, Any]:
        category = self._normalize_category(request.category or self._config.category)
        common: dict[str, Any] = {
            "model_image": self._encode_file(request.person_image),
            "seed": request.seed,
            "output_format": self._config.output_format,
            "return_base64": self._config.return_base64,
        }
        if self._config.model_name == "tryon-max":
            return self._without_none(
                {
                    **common,
                    "product_image": self._encode_file(request.garment_image),
                    "generation_mode": "quality" if self._config.mode == "quality" else "balanced",
                    "num_images": self._config.num_samples,
                }
            )
        return self._without_none(
            {
                **common,
                "garment_image": self._encode_file(request.garment_image),
                "category": category,
                "segmentation_free": self._config.segmentation_free,
                "moderation_level": self._config.moderation_level,
                "garment_photo_type": self._config.garment_photo_type,
                "mode": self._config.mode,
                "num_samples": self._config.num_samples,
            }
        )

    @staticmethod
    def _encode_file(path: Path) -> str:
        mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    @staticmethod
    def _normalize_base_url(api_url: str) -> str:
        base_url = api_url.rstrip("/")
        return base_url if base_url.endswith("/v1") else f"{base_url}/v1"

    @staticmethod
    def _normalize_category(category: str) -> str:
        mapping = {
            "auto": "auto",
            "tops": "tops",
            "bottoms": "bottoms",
            "one-pieces": "one-pieces",
            "dress": "one-pieces",
            "outerwear": "tops",
            "shoes": "auto",
            "accessory": "auto",
        }
        return mapping.get(category, "auto")

    @staticmethod
    def _without_none(payload: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in payload.items() if value is not None}

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }

    def _write_output(self, job_id: str, output: str) -> Path:
        suffix = self._config.output_format if self._config.output_format in {"png", "jpeg"} else "png"
        extension = "jpg" if suffix == "jpeg" else suffix
        output_path = Path("outputs/baseline") / f"fashn-{job_id}.{extension}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output.startswith("data:image/"):
            try:
                _, encoded = output.split(",", 1)
                output_path.write_bytes(base64.b64decode(encoded))
            except (ValueError, binascii.Error) as exc:
                raise BaselineProviderError("FASHN returned invalid base64 image output") from exc
            return output_path
        image_response = self._client.get(output)
        self._raise_for_api_error(image_response)
        output_path.write_bytes(image_response.content)
        return output_path

    @staticmethod
    def _raise_for_api_error(response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        error = payload.get("error", response.reason_phrase)
        message = payload.get("message", response.text)
        raise BaselineProviderError(f"FASHN API error {response.status_code}: {error} - {message}")

    @staticmethod
    def _require_string(payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise BaselineProviderError(f"FASHN response missing string field: {key}")
        return value

    @staticmethod
    def _require_output(payload: dict[str, Any]) -> list[str]:
        output = payload.get("output")
        if not isinstance(output, list) or not output or not all(isinstance(item, str) for item in output):
            raise BaselineProviderError("FASHN completed without a valid output array")
        return output

    @staticmethod
    def _validate_request(request: TryOnRequest) -> None:
        for path in [request.person_image, request.garment_image]:
            if not path.exists():
                raise FileNotFoundError(f"Baseline input does not exist: {path}")

    @staticmethod
    def _format_error(error: object) -> str:
        if isinstance(error, dict):
            name = error.get("name", "RuntimeError")
            message = error.get("message", "")
            return f"{name}: {message}".strip()
        return str(error)
