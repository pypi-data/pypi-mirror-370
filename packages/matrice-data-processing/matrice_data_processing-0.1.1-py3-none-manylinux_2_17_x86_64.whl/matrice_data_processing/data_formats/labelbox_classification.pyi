"""Auto-generated stub for module: labelbox_classification."""
from typing import Any, List, Tuple

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
def add_labelbox_classification_dataset_item_local_file_path(batch_dataset_items: Any, base_dataset_path: Any) -> Any: ...
    """
    Add local file paths to dataset items and download missing images.
    
        Args:
            batch_dataset_items: List of dataset items to process
            base_dataset_path: Base path for dataset storage
    
        Returns:
            List of processed dataset items with local file paths
    """
def add_labelbox_classification_dataset_items_details(batch_dataset_items: Any, images_details: Any) -> Any: ...
    """
    Add image details to batch dataset items.
    
        Args:
            batch_dataset_items: List of dataset items to process
            images_details: Dictionary of image details indexed by image filename
    
        Returns:
            List of processed dataset items with added details
    """
def download_labelbox_classification_dataset(dataset_id: Any, labelbox_annotations_path: Any) -> Any: ...
    """
    Download Labelbox dataset and organize it into a structured format.
    
        Args:
            dataset_id: Identifier for the dataset
            labelbox_annotations_path: Path to the annotations file
    
        Returns:
            Dataset ID
    """
def download_labelbox_classification_images(images_path: Any, labelbox_annotations_path: Any) -> Any: ...
    """
    Download Labelbox images from annotation file and save them.
    
        Args:
            images_path: Path to save downloaded images
            labelbox_annotations_path: Path to the annotations file
    """
def get_labelbox_classification_image_details(annotation_files: Any) -> Any: ...
    """
    Process Labelbox NDJSON annotation files and extract image details.
    
        Args:
            annotation_files: List of paths to Labelbox NDJSON annotation files
    
        Returns:
            Tuple containing:
            - Dictionary of image details indexed by file location
            - List of image entries missing annotations
            - Dictionary of class-wise splits
    """
def load_ndjson(file_path: Any) -> Any: ...
    """
    Read an NDJSON file and extract valid JSON objects.
    
        Args:
            file_path: Path to the NDJSON file
    
        Returns:
            List of parsed JSON objects
    """
