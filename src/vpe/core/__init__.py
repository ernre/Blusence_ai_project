"""VPE inference core components."""

from vpe.core.attention import DecoupledCrossAttention
from vpe.core.engine import VPEngine
from vpe.core.garment_encoder import GarmentEncoder, GarmentFeatures
from vpe.core.multiview import CrossViewAttentionBlock
from vpe.core.pose import PoseConditioner

__all__ = [
    "CrossViewAttentionBlock",
    "DecoupledCrossAttention",
    "GarmentEncoder",
    "GarmentFeatures",
    "PoseConditioner",
    "VPEngine",
]
