"""Auto-generated stub for module: snow."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class SnowAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, brightness_coeff: Any = 2.5, snow_point_range: Any = [0.1, 0.3], method: Any = 'bleach', prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

