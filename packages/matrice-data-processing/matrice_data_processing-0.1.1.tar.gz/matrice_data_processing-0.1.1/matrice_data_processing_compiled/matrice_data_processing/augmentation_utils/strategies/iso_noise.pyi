"""Auto-generated stub for module: iso_noise."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class ISONoiseAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, color_shift: Any = (0.01, 0.05), intensity: Any = (0.1, 0.5), prob: float = 0.5) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

