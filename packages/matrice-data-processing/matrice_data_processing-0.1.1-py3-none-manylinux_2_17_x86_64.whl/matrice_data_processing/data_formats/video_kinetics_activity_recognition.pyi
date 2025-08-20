"""Auto-generated stub for module: video_kinetics_activity_recognition."""
from typing import Any, List, Tuple

from matrice_data_processing.server_utils import get_corresponding_split_type, generate_short_uuid
from uuid import uuid4
import csv
import cv2
import logging
import os
import requests
import tempfile

# Functions
def add_kinetics_dataset_items_details(batch_dataset_items: Any, frames_details: Any) -> Any: ...
    """
    Add details to kinetics dataset items.
    
        Args:
            batch_dataset_items: Batch of dataset items to process
            frames_details: Details of frames from annotations
    
        Returns:
            List of processed dataset items
    """
def get_kinetics_annotations(annotation_paths: Any) -> Any: ...
    """
    Process Kinetics-style dataset and return video annotations grouped by video and split.
    """
def get_kinetics_dataset_item_details(image_path: Any) -> Any: ...
    """
    Get split and category from image path.
    
        Args:
            image_path: Path to the image file
    
        Returns:
            Tuple of (split, category)
    """
def get_video_metadata(presigned_url: Any) -> Any: ...
    """
    Downloads a video from a presigned URL, extracts its dimensions (width, height),
    FPS, and duration, and saves the first frame as an image locally.
    
    Args:
        presigned_url (str): The presigned URL of the video.
    
    Returns:
        dict: {
            "width": video_width,
            "height": video_height,
            "fps": rounded_fps,
            "first_frame_path": path_to_saved_image
        }
    """
