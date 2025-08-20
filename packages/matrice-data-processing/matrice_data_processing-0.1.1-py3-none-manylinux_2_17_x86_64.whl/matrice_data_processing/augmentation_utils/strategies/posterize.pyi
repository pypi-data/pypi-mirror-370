"""Auto-generated stub for module: posterize."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class PosterizeAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, num_bits: Any = 4, prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

