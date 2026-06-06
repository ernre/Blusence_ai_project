"""VPE inference core components."""

from vpe.core.attention import DecoupledCrossAttention
from vpe.core.engine import VPEngine
from vpe.core.garment_encoder import GarmentEncoder, GarmentFeatures
from vpe.core.lora import BrandLoRAAdapter, BrandLoRALoader, BrandLoRARegistry
from vpe.core.multiview import CrossViewAttentionBlock
from vpe.core.pose import PoseConditioner

__all__ = [
    "CrossViewAttentionBlock",
    "DecoupledCrossAttention",
    "BrandLoRAAdapter",
    "BrandLoRALoader",
    "BrandLoRARegistry",
    "GarmentEncoder",
    "GarmentFeatures",
    "PoseConditioner",
    "VPEngine",
]
