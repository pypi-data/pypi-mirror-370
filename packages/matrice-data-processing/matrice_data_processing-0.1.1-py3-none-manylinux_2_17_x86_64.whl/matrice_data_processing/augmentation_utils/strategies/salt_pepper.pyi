"""Auto-generated stub for module: salt_pepper."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class SaltAndPepperNoiseAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, amount_range: Any = [0.01, 0.06], salt_vs_pepper_range: Any = [0.4, 0.6], prob: float = 0.5) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

