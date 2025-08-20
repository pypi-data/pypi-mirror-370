"""Auto-generated stub for module: shadows."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class ShadowAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, prob: float = 1.0, shadow_roi_x: Any = [0, 1], shadow_roi_y: Any = [0, 1], num_shadows_limit: Any = [2, 3], shadow_dimension: Any = 4, shadow_intensity_range: Any = [0.2, 0.7]) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

