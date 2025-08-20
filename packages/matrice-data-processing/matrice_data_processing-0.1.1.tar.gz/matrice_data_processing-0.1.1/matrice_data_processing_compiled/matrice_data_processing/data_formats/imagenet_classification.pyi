"""Auto-generated stub for module: imagenet_classification."""
from typing import Any, List, Tuple

from collections import defaultdict
from matrice_data_processing.server_utils import generate_short_uuid
from matrice_data_processing.server_utils import get_corresponding_split_type
import logging
import os

# Functions
def add_imagenet_dataset_items_details(batch_dataset_items: Any) -> Any: ...
    """
    Add ImageNet-specific details to dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to process
    
        Returns:
            List of processed dataset items with added details
    """
def get_classwise_splits_imagenet(dataset_items_batches: Any) -> Any: ...
    """
    Count images per category and split in ImageNet dataset.
    
        Args:
            dataset_items_batches: Batches of dataset items
    
        Returns:
            Dictionary of class-wise split counts or None if no classes found
    """
def get_imagenet_dataset_item_details(image_path: Any) -> Any: ...
    """
    Extract details from an ImageNet image path.
    
        Args:
            image_path: Path to the image file
    
        Returns:
            Tuple containing:
            - split: Dataset split (train, val, test, or unassigned)
            - category: Image category
            - annotations: List of annotation objects
    """
