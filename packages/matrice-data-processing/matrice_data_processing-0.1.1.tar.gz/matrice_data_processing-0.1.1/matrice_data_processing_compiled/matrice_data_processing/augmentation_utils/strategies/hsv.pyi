"""Auto-generated stub for module: hsv."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class HueSaturationValueAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, prob: float = 0.5, hue_shift_limit: Any = [-20, 20], sat_shift_limit: Any = [-30, 30], val_shift_limit: Any = [-20, 20]) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

