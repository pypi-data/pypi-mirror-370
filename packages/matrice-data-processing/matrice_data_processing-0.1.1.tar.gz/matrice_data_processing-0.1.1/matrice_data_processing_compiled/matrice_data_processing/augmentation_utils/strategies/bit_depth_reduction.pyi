"""Auto-generated stub for module: bit_depth_reduction."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import logging
import numpy as np

# Classes
class BitDepthReductionAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, bit_depth: int = 4, prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

