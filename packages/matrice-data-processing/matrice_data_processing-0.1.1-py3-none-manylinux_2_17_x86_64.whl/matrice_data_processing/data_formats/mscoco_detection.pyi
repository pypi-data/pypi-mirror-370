"""Auto-generated stub for module: mscoco_detection."""
from typing import Any, List

from matrice_data_processing.server_utils import get_corresponding_split_type, generate_short_uuid
import json
import logging
import os
import traceback

# Functions
def add_mscoco_dataset_items_details(batch_dataset_items: Any, images_details: Any) -> Any: ...
    """
    Add image details to batch dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to process
            images_details: Dictionary of image details indexed by split and filename
    
        Returns:
            List of processed dataset items with image details
    """
def calculate_bbox_properties(bbox: Any) -> Any: ...
    """
    Calculate properties for a bounding box.
    
        Args:
            bbox: Bounding box in format [x_min, y_min, width, height]
    
        Returns:
            Dictionary containing height, width, center coordinates, and area
    
        Raises:
            ValueError: If bbox doesn't have exactly 4 elements
    """
def get_msococ_annotation_details(annotations: Any, image_info: Any, category_map: Any, split_type: Any) -> Any: ...
    """
    Process annotations and extract detailed properties.
    
        Args:
            annotations: List of annotation objects
            image_info: Dictionary mapping image IDs to image details
            category_map: Dictionary mapping category IDs to category names
            split_type: Dataset split type (train, val, test)
    
        Returns:
            Dictionary of annotation details by image key
    """
def get_msococo_images_details(annotation_files: Any) -> Any: ...
    """
    Process MSCOCO annotation files and extract image details.
    
        Args:
            annotation_files: List of paths to MSCOCO annotation JSON files
    
        Returns:
            Dictionary of image details indexed by file location
    """
