"""Auto-generated stub for module: yolo_detection."""
from typing import Any, List, Tuple

from matrice_data_processing.server_utils import get_corresponding_split_type, generate_short_uuid
import logging
import os
import re
import traceback
import yaml

# Functions
def add_yolo_dataset_items_details(batch_dataset_items: Any, images_details: Any) -> Any: ...
    """
    Add image details to batch dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to process
            images_details: Dictionary of image details indexed by filename
    
        Returns:
            List of processed dataset items with added details
    """
def convert_payload_to_coco_format(payload: Any) -> Any: ...
    """
    Convert YOLO bbox format in payload to MS COCO format.
    
        Args:
            payload: The original payload containing YOLO bbox details
    
        Returns:
            Updated payload with COCO bbox format
    """
def get_yolo_image_details(annotation_files: Any) -> Any: ...
    """
    Process YOLO annotation files and extract image details.
    
        Args:
            annotation_files: List of paths to YOLO annotation files (.txt) and data.yaml
    
        Returns:
            Tuple containing:
            - Dictionary of image details indexed by file location
            - List of image filenames missing annotations
            - Dictionary of class-wise splits from data.yaml
    """
def yolo_to_coco_bbox(yolo_bbox: Any, img_width: Any, img_height: Any) -> Any: ...
    """
    Convert YOLO bbox format to MS COCO format.
    
        Args:
            yolo_bbox: List containing [x_center, y_center, width, height] (normalized)
            img_width: Image width in pixels
            img_height: Image height in pixels
    
        Returns:
            Tuple containing:
            - coco_bbox: List [x_min, y_min, width, height]
            - coco_bbox_height: Height in absolute pixels
            - coco_bbox_width: Width in absolute pixels
            - coco_bbox_center: List [x_center, y_center] in absolute pixels
            - coco_bbox_area: Area in square pixels
    """
