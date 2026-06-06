"""Try-on provider registry."""

from vpe.providers.base import ProviderDescriptor, ProviderUnavailableError, TryOnProvider
from vpe.providers.fashn import FashnBenchmarkProvider, FashnConfig
from vpe.providers.idm_vton import IDMVTONConfig, IDMVTONResearchProvider
from vpe.providers.local import LocalPreviewProvider
from vpe.providers.registry import active_provider_id, build_tryon_provider, provider_descriptors

__all__ = [
    "FashnBenchmarkProvider",
    "FashnConfig",
    "IDMVTONConfig",
    "IDMVTONResearchProvider",
    "LocalPreviewProvider",
    "ProviderDescriptor",
    "ProviderUnavailableError",
    "TryOnProvider",
    "active_provider_id",
    "build_tryon_provider",
    "provider_descriptors",
]
