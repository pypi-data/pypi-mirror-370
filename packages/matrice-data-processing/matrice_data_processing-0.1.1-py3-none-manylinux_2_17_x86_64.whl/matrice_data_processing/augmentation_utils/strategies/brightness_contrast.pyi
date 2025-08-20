"""Auto-generated stub for module: brightness_contrast."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class BrightnessContrastAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, prob: float = 1.0, brightness_limit: Any = [-0.2, 0.2], contrast_limit: Any = [-0.2, 0.2], brightness_by_max: Any = True, ensure_safe_range: Any = False) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

