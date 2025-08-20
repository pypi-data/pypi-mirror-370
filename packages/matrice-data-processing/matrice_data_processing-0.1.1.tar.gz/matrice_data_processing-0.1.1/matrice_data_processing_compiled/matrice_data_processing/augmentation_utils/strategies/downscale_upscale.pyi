"""Auto-generated stub for module: downscale_upscale."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class DownscaleUpscaleAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, scale_min: Any = 0.25, scale_max: Any = 0.5, upscale: int = 0, downscale: int = 0, prob: float = 0.5) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

