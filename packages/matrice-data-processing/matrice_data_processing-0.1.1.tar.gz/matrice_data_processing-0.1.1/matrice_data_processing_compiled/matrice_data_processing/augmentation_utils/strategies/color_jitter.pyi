"""Auto-generated stub for module: color_jitter."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class ColorJitterAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, brightness: Any = [0.8, 1.2], contrast: Any = [0.8, 1.2], saturation: Any = [0.8, 1.2], hue: Any = [-0.5, 0.5], prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

