"""Auto-generated stub for module: random_affine."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import cv2
import logging
import numpy as np

# Functions
def strat_map(strategy: str) -> str: ...
    """
    Map strategy name to its corresponding class.
    """

# Classes
class RandomAffineAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, prob: float = 0.5, shift_limit: Any = [-0.0625, 0.0625], scale_limit: Any = [-0.1, 0.1], rotate_limit: Any = [-45, 45], interpolation: Any = cv2.INTER_LINEAR, border_mode: Any = cv2.BORDER_CONSTANT, rotate_method: Any = 'ellipse', mask_interpolation: Any = 0, fill: Any = 0, fill_mask: Any = 0) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

