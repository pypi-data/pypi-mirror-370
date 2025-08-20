"""Auto-generated stub for module: low_light."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import logging
import numpy as np

# Classes
class LowLightSimulationAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, brightness_factor: Any = 0.3, prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

