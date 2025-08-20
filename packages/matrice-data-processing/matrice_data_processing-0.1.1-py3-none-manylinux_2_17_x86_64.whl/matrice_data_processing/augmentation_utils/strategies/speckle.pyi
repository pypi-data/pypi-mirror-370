"""Auto-generated stub for module: speckle."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import logging
import numpy as np

# Classes
class SpeckleNoiseAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, prob: float = 1.0, mean: float = 0.0, var: float = 0.01) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

