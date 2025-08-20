"""Auto-generated stub for module: rain."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class RainAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, slant_range: Any = [-15, 15], drop_length: Any = 50, drop_width: Any = 1, red_drop_color: Any = 200, green_drop_color: Any = 255, blue_drop_color: Any = 255, blur_value: Any = 7, brightness_coefficient: Any = 0.7, rain_type: Any = 'default', prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

