"""Auto-generated stub for module: video_youtube_bb_tracking."""
from typing import Any, List, Tuple

from PIL import Image
from io import BytesIO
from matrice_data_processing.server_utils import get_corresponding_split_type, generate_short_uuid
import logging
import os
import pandas as pd
import re
import requests

# Functions
def add_youtube_bb_dataset_items_details(batch_dataset_items: Any, frames_details: Any) -> Any: ...
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
def extract_video_identifier(file_name: Any) -> Any: ...
    """
    Extract video identifier from a filename.
    
        Args:
            file_name: Filename to extract the identifier from
    
        Returns:
            Video identifier string (part before the last underscore)
    """
def get_image_dimensions_from_url(presigned_url: Any) -> Any: ...
    """
    Get image dimensions from a URL.
    
        Args:
            presigned_url: URL of the image to analyze
    
        Returns:
            Tuple containing height and width or (None, None) on failure
    """
def get_youtube_bb_video_frame_details(dataset_path: Any) -> Any: ...
    """
    Process YouTube Bounding Box dataset and extract details for each video sequence.
    
        Args:
            dataset_path: List of paths to CSV annotation files
    
        Returns:
            Tuple containing:
            - Dictionary of video details indexed by youtube_id
            - List of frames missing annotations
            - Dictionary of class-wise statistics
    """
def preprocess_frames_details(frames_details: Any) -> Any: ...
    """
    Preprocess frames details into a lookup structure.
    
        Args:
            frames_details: Dictionary of frame details by video identifier
    
        Returns:
            Lookup dictionary mapping (video_id, frame_id) tuples to frame data
    """
