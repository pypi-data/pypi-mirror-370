"""Auto-generated stub for module: pascalvoc_detection."""
from typing import Any, List, Tuple

from matrice_data_processing.server_utils import generate_short_uuid
import logging
import os
import xml.etree.ElementTree as ET

# Functions
def add_pascalvoc_dataset_items_details(batch_dataset_items: Any, images_details: Any) -> Any: ...
    """
    Add image details to batch dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to process
            images_details: Dictionary of image details indexed by filename
    
        Returns:
            List of processed dataset items with details added
    """
def calculate_pascal_bbox_properties(bbox: Any) -> Any: ...
    """
    Calculate properties for Pascal VOC bounding box.
    
        Args:
            bbox: Bounding box in format [x_min, y_min, x_max, y_max]
    
        Returns:
            Dictionary of properties including bbox, height, width, center, area
    
        Raises:
            ValueError: If bbox doesn't have exactly 4 elements
    """
def get_pascalvoc_image_details(annotation_files: Any) -> Any: ...
    """
    Process Pascal VOC annotation files and extract image details.
    
        Args:
            annotation_files: List of paths to Pascal VOC annotation files (XML and TXT)
    
        Returns:
            Tuple containing:
            - Dictionary of image details indexed by file location
            - List of image filenames missing annotations
            - Dictionary of class-wise splits
    """
