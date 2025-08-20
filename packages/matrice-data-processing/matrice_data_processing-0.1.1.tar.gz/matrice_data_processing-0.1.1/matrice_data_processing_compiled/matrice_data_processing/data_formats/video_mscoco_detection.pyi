"""Auto-generated stub for module: video_mscoco_detection."""
from typing import Any, List, Tuple

from matrice_data_processing.server_utils import get_corresponding_split_type, generate_short_uuid
import json
import logging
import os
import traceback

# Functions
def add_mscoco_dataset_items_details(batch_dataset_items: Any, frames_details: Any) -> Any: ...
    """
    Enhance batch dataset items with corresponding frame annotations.
    
        Args:
            batch_dataset_items: List of dataset items to enhance
            frames_details: Dictionary of frame details by video identifier
    
        Returns:
            Processed batch with added details
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
def get_msococo_videos_details(annotation_files: Any) -> Any: ...
    """
    Process MSCOCO video annotation files and extract video details.
    
        Args:
            annotation_files: List of paths to MSCOCO video annotation JSON files
    
        Returns:
            Tuple containing:
            - Dictionary of video details indexed by file location
            - List of video IDs missing annotations
            - Dictionary of class-wise split counts
    """
