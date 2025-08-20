"""Auto-generated stub for module: sunflare."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class SunFlareAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, flare_roi: Any = (0.0, 0.0, 1.0, 0.5), angle_lower: Any = 0.0, angle_upper: Any = 1.0, num_flare_circles_lower: Any = 6, prob: float = 0.5) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

