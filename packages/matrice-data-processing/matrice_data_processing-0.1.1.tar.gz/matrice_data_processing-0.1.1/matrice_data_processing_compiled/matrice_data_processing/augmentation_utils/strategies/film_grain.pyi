"""Auto-generated stub for module: film_grain."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class FilmGrainAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, std_range: Any = [0.1, 0.2], mean_range: Any = [0, 0], per_channel: Any = True, noise_scale_factor: Any = 1, prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

