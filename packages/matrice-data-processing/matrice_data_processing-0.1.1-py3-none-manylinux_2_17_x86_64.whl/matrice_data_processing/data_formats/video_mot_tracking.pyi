"""Auto-generated stub for module: video_mot_tracking."""
from typing import Any, List, Tuple

from collections import defaultdict
import configparser
import logging
import os

# Functions
def add_mot_dataset_items_details(batch_dataset_items: Any, frames_details: Any) -> Any: ...
    """
    Enhance batch dataset items with corresponding frame annotations.
    
        Args:
            batch_dataset_items: List of dataset items to enhance
            frames_details: Dictionary of frame details by video identifier
    
        Returns:
            Processed batch with added details
    """
def calculate_mot_bbox_properties(bbox: Any) -> Any: ...
    """
    Calculate properties for MOT bounding box.
    
        Args:
            bbox: List containing [x, y, width, height]
    
        Returns:
            Dictionary containing bbox properties (bbox, height, width, center, area)
    """
def extract_video_identifier(path: Any) -> Any: ...
    """
    Extract the video name from the file path.
    
        Args:
            path: File path to extract video identifier from
    
        Returns:
            Video identifier string or None if path is invalid
    """
def get_mot_annotations(dataset_paths: Any) -> Any: ...
    """
    Process MOT dataset and extract video annotations.
    
        Args:
            dataset_paths: List of paths to MOT dataset files
    
        Returns:
            Tuple containing:
            - Dictionary of complete video information by video name
            - Dictionary of class statistics
    """
def parse_gt(gt_path: Any, img_dir: Any) -> Any: ...
    """
    Parse gt.txt file to extract annotations.
    
        Args:
            gt_path: Path to the ground truth file
            img_dir: Directory containing the images
    
        Returns:
            Dictionary mapping frame IDs to lists of annotations
    """
def parse_seqinfo(seqinfo_path: Any) -> Any: ...
    """
    Parse seqinfo.ini file to extract video metadata.
    
        Args:
            seqinfo_path: Path to the seqinfo.ini file
    
        Returns:
            Dictionary containing video metadata or empty dict if parsing fails
    """
def rename_mot_file(file_path: Any) -> Any: ...
    """
    Rename MOT dataset files to include split and video information.
    
        Args:
            file_path: Path to the file to rename
    
        Returns:
            New path after renaming
    
        Raises:
            ValueError: If video folder cannot be determined from path
    """
