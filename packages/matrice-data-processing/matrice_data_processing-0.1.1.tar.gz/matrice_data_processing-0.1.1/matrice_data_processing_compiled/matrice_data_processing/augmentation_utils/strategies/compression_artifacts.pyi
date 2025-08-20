"""Auto-generated stub for module: compression_artifacts."""
from typing import Any, List, Tuple

from base import ImageAugmentationStrategy
import albumentations as A
import logging
import numpy as np

# Classes
class CompressionArtifactsAugmentation(ImageAugmentationStrategy):
    def __init__(self: Any, quality_range: Any = [50, 20], prob: float = 1.0) -> None: ...

    def apply(self: Any, image: Any, bboxes: Any, bbox_format: Any = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

