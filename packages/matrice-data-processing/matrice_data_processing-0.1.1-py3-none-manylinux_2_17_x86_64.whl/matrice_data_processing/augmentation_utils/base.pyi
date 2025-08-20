"""Auto-generated stub for module: base."""
from typing import Any, Dict, List, Tuple

from abc import ABC, abstractmethod
import numpy as np

# Functions
def yolo_to_mscoco(bboxes: List[List[float]], image_width: int, image_height: int) -> List[List[float]]: ...
    """
    Converts YOLO format bounding boxes to MSCOCO format.
    
    Args:
        bboxes (List[List[float]]): List of bounding boxes in YOLO format [x_center, y_center, width, height].
        image_width (int): Width of the image.
        image_height (int): Height of the image.
    
    Returns:
        List[List[float]]: List of bounding boxes in MSCOCO format [x_min, y_min, width, height].
    """

# Classes
class ImageAugmentationStrategy(ABC):
    def apply(self: Any, image: Any, bboxes: List[List[float]], bbox_format: str = 'coco') -> Tuple[np.ndarray, int, int, List[List[float]]]: ...

