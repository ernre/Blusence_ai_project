"""Baseline VTON adapter interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from vpe.types import TryOnRequest, TryOnResult


class BaselineVTON(ABC):
    """Interface for external VTON baseline providers."""

    @abstractmethod
    def render(self, request: TryOnRequest) -> TryOnResult:
        """Generate a baseline try-on image."""
