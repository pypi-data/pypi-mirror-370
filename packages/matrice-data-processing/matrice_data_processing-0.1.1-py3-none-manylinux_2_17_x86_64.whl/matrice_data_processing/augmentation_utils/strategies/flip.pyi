"""Auto-generated stub for module: flip."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class HorizontalFlipAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, prob: float = 0.5) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]]) -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

