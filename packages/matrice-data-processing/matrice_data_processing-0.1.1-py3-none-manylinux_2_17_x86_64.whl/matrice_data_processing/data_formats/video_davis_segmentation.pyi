"""Auto-generated stub for module: video_davis_segmentation."""
from typing import Any, List, Tuple

from collections import defaultdict
from matrice_data_processing.server_utils import generate_short_uuid, get_corresponding_split_type
import cv2
import logging
import numpy as np
import os

# Functions
def add_davis_dataset_items_details(batch_dataset_items: Any, frames_details: Any) -> Any: ...
    """
    Enhance batch dataset items with corresponding frame annotations.
    
        Args:
            batch_dataset_items: List of dataset items to enhance
            frames_details: Dictionary of frame details by video identifier
    
        Returns:
            Processed batch with added details
    """
def extract_objects_from_mask(mask_path: Any, video_name: Any) -> Any: ...
    """
    Extract object bounding boxes, polygon segmentations, and properties from a grayscale mask.
    
        Args:
            mask_path: Path to the segmentation mask image
    
        Returns:
            Tuple containing:
            - List of annotation objects
            - Video height
            - Video width
    
        Raises:
            ValueError: If the mask image cannot be loaded
    """
def extract_video_identifier(path: Any) -> Any: ...
    """
    Extract the video name from the file path.
    
        Args:
            path: File path to extract video identifier from
    
        Returns:
            Video identifier string or None if path is invalid
    """
def get_davis_annotations(dataset_paths: Any) -> Any: ...
    """
    Process DAVIS dataset and extract video annotations.
    
        Args:
            dataset_paths: List of paths to dataset files
    
        Returns:
            Tuple containing:
            - Dictionary of complete video information indexed by video name
            - Dictionary of video counts by split
    """
def read_dataset_splits(dataset_paths: Any) -> Any: ...
    """
    Reads train.txt, val.txt, and test.txt to map videos to dataset splits.
    
        Args:
            dataset_paths: List of paths to dataset files
    
        Returns:
            Dictionary mapping video names to their respective splits
    """
def rename_davis_file(file_path: Any) -> Any: ...
    """
    Rename Davis dataset files to a standardized format.
    
        Args:
            file_path: Path to the file to rename
    
        Returns:
            New path after renaming
    """
