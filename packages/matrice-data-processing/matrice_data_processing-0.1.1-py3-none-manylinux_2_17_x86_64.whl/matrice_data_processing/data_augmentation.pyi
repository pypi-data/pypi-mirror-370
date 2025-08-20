"""Auto-generated stub for module: data_augmentation."""
from typing import Any, Dict, List

from matrice_data_processing.client import add_batch_presigned_upload_urls, upload_batch_files
from matrice_data_processing.client_utils import update_partitions_numbers, create_partition_stats, SAMPLES_PARTITION_TYPE
from matrice_data_processing.data_prep import dataset_items_producer
from matrice_data_processing.image_augmentations import get_augmentation_compose
from matrice_data_processing.pipeline import Pipeline
from matrice_data_processing.server_utils import download_file, generate_short_uuid
from queue import Queue
import cv2
import logging
import os

# Functions
def augment_dataset_items(batch_dataset_items: Any, augmentation_fns: Any) -> Any: ...
def batch_insert_dataset_items(batch: Any, dataset_id: Any, rpc: Any) -> Any: ...
def calculate_partition_stats(dataset_items: List[Dict]) -> List[Dict]: ...
    """
    Calculate partition statistics for dataset items.
    
        Args:
            dataset_items: List of dataset items
    """
def create_augmentation_fns(augmentation_configs: Dict) -> List[callable]: ...
    """
    Create a function to perform data augmentation.
    
        Args:
            augmentation_configs: Dictionary containing augmentation parameters
    
        Returns:
            List of augmentation functions
    """
def download_images(dataset_items: List[Dict]) -> List[Dict]: ...
    """
    Download images for dataset items.
    
        Args:
            dataset_items: List of dataset items containing file locations and names
    
        Returns:
            List of successfully downloaded items
    """
def filter_dataset_items(batch_dataset_items: Dict[str, List], dataset_version: str = 'v1.0') -> List[Dict]: ...
    """
    Filter dataset items based on the set type (train/test/val).
    
        Args:
            dataset_items: Dictionary containing version info and items
            dataset_version: Version string to filter by
    
        Returns:
            List of training items for the specified version
    """
def get_data_augmentation_pipeline(rpc: Any, dataset_id: str, dataset_version: str, augmentation_configs: list, max_attempts: int = 5, bucket_alias: str = '', account_number: str = '') -> Any: ...
    """
    Get the data augmentation pipeline.
    
        Args:
            rpc: RPC client for making API calls
            dataset_id: Dataset ID
            dataset_version: Dataset version
            augmentation_configs: List of augmentation configurations
            max_attempts: Maximum number of upload retry attempts
            bucket_alias: Storage bucket alias
            account_number: Account number for storage access
    
        Returns:
            Configured Pipeline object for data augmentation
    """
def load_bboxes(dataset_item: Any) -> Any: ...
def load_image(dataset_item: Any) -> Any: ...
def save_augmented_images(batch_dataset_items: Any, dataset_id: Any) -> Any: ...

# Classes
class DataAugmentation:
    """
    Class to handle dataset preparation.
    """

    def __init__(self: Any, session: Any, action_record_id: str) -> None: ...
        """
        Initialize DataAugmentation.
        
                Args:
                    session: Session object with RPC client
                    action_record_id: ID of action record
        """

    def start_processing(self: Any) -> None: ...
        """
        Start dataset augmentation processing.
        """

    def update_status(self: Any, stepCode: str, status: str, status_description: str) -> None: ...
        """
        Update status of data preparation.
        
                Args:
                    stepCode: Code indicating current step
                    status: Status of step
                    status_description: Description of status
        """

