"""Auto-generated stub for module: blur."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class BlurAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, blur_limit: int = 5, prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: str = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

