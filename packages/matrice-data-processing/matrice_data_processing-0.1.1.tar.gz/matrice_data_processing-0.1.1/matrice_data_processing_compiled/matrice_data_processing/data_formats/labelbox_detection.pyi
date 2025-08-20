"""Auto-generated stub for module: labelbox_detection."""
from typing import Any, List

from concurrent.futures import ThreadPoolExecutor
from matrice_data_processing.server_utils import generate_short_uuid, download_file
from urllib.parse import urlparse
import json
import logging
import os
import re
import requests
import shutil
import traceback

# Functions
def add_labelbox_dataset_item_local_file_path(batch_dataset_items: Any, base_dataset_path: Any) -> Any: ...
    """
    Add local file paths to dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to process
            base_dataset_path: Base path for dataset
    
        Returns:
            List of processed dataset items with local file paths added
    """
def add_labelbox_dataset_items_details(batch_dataset_items: Any, images_details: Any) -> Any: ...
    """
    Add image details to batch dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to process
            images_details: Dictionary of image details indexed by file name
    
        Returns:
            List of processed dataset items with details added
    """
def calculate_bbox_properties(bbox: Any) -> Any: ...
    """
    Calculate properties for a bounding box.
    
        Args:
            bbox: Bounding box in format [x_min, y_min, width, height]
    
        Returns:
            Dictionary of properties including height, width, center, area
    
        Raises:
            ValueError: If bbox doesn't have exactly 4 elements
    """
def download_labelbox_dataset_items(dataset_id: Any, labelbox_annotations_path: Any) -> Any: ...
    """
    Download Labelbox dataset from the given annotation path and save it to the base dataset path
    
    Args:
        dataset_id: ID for the dataset
        labelbox_annotations_path: Path to the labelbox annotations file
    
    Returns:
        Dataset ID
    """
def download_labelbox_images(images_path: Any, labelbox_annotations_path: Any) -> Any: ...
    """
    Download Labelbox images from the given annotation path and save them to the images path.
    Uses multithreading to download images in parallel.
    
    Args:
        images_path: Path to save the downloaded images
        labelbox_annotations_path: Path to the labelbox annotations file
    """
def get_labelbox_image_details(annotation_files: Any) -> Any: ...
    """
    Process Labelbox NDJSON annotation files and extract image details.
    
        Args:
            annotation_files (list): List of paths to Labelbox NDJSON annotation files.
    
        Returns:
            tuple:
            - Dictionary of image details indexed by file location.
            - List of image entries missing annotations.
            - Dictionary of class-wise splits.
    """
def load_ndjson(file_path: Any) -> Any: ...
    """
    Reads an NDJSON file and extracts valid JSON objects.
    
        Args:
            file_path: Path to the NDJSON file
    
        Returns:
            List of parsed JSON objects
    """
