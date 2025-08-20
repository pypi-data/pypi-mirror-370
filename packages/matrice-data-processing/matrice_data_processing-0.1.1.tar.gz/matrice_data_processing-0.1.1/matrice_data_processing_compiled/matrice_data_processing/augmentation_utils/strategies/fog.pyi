"""Auto-generated stub for module: fog."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class FogAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, alpha_coef: Any = 0.1, fog_coef_range: Any = [0.1, 0.5], prob: float = 0.5) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

