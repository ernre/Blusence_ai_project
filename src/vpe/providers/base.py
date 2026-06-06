"""Provider contracts for product, benchmark, and research try-on engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from vpe.types import TryOnRequest, TryOnResult


class ProviderUnavailableError(RuntimeError):
    """Raised when a configured provider cannot run in the current environment."""


@dataclass(frozen=True)
class ProviderDescriptor:
    """Public metadata for a try-on provider."""

    id: str
    label: str
    role: str
    status: str
    requires: tuple[str, ...] = ()
    notes: str = ""


class TryOnProvider(ABC):
    """Common interface for all try-on providers."""

    descriptor: ProviderDescriptor

    @abstractmethod
    def render(self, request: TryOnRequest) -> TryOnResult:
        """Render a try-on image from normalized request inputs."""
