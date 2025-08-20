"""Auto-generated stub for module: server_utils."""
from typing import Any, Dict, List, Optional, Tuple

from collections import defaultdict
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from matrice_data_processing.client_utils import is_file_compressed
from urllib.parse import urlparse
import base64
import logging
import logging
import math
import os
import requests
import shutil
import tarfile
import time
import traceback
import uuid
import zipfile

# Functions
def chunk_items(items: List[Dict[str, Any]], chunk_size: int) -> List[List[Dict[str, Any]]]: ...
    """
    Chunk items into smaller batches.
    
    Args:
        items: List of items to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunked item batches
    """
def construct_relative_path(dataset_id: str, folder_name: str, file_name: str) -> str: ...
    """
    Construct relative path from components.
    
    Args:
        dataset_id: Dataset identifier
        folder_name: Name of folder
        file_name: Name of file
    
    Returns:
        Constructed relative path
    """
def delete_tmp_folder(tmp_folder_path: str) -> None: ...
    """
    Delete temporary folder.
    
    Args:
        tmp_folder_path: Path to temporary folder
    """
def download_file(url: str, file_path: str, timeout: int = 60, chunk_size: int = 8192, max_retries: int = 1) -> str: ...
    """
    Download file from URL to specified path with improved reliability.
    
    Args:
        url: URL to download from
        file_path: Path to save file to
        timeout: Request timeout in seconds
        chunk_size: Size of chunks to download
    
    Returns:
        Path where file was saved
    
    Raises:
        Exception: If download fails
    """
def enrich_items_with_file_info(rpc: Any, items: List[Dict[str, Any]], download_images_required: bool = False) -> List[Dict[str, Any]]: ...
    """
    Enriches dataset items with file and annotation information, including presigned URLs if requested.
    
    Args:
        rpc: RPC client for making API calls
        items: List of dataset items to enrich
        download_images_required: Whether to get presigned URLs for images
    
    Returns:
        List of enriched dataset items
    """
def extract_dataset(dataset_path: str, get_inner_dir: bool = False) -> str: ...
    """
    Extract compressed dataset.
    
    Args:
        dataset_path: Path to compressed dataset
        get_inner_dir: Whether to return inner directory path
    
    Returns:
        Path to extracted dataset
    
    Raises:
        ValueError: If archive format is unsupported
        Exception: If extraction fails
    """
def extract_davis_video_name(file_path: str) -> str: ...
def fetch_all_annotations(rpc: Any, dataset_item_id: str, version: str) -> List[Dict[str, Any]]: ...
def fetch_all_file_info(rpc: Any, dataset_item_id: str) -> List[Dict[str, Any]]: ...
def fetch_annotation_info(rpc: Any, dataset_item_id: str, version: str, page_size: int = 10) -> List[Dict[str, Any]]: ...
    """
    Fetches all annotation information for a specific dataset item and version across pages.
    
    Args:
        rpc: RPC client for making API calls
        dataset_item_id: Dataset item identifier
        version: Version identifier
        page_size: Number of items per page
    
    Returns:
        A list of all annotation information items
    """
def fetch_base_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, page_size: int) -> List[Dict[str, Any]]: ...
def fetch_data_prep_video_frame_items(rpc: Any, path: str, request_batch_size: int, page_number: Optional[int] = None, download_images_required: bool = True, is_file_info_required: bool = True, isAnnotationInfoRequired: bool = True) -> List[Dict[str, Any]]: ...
    """
    Fetch video frame items from the dataset API.
    
    Args:
        rpc: RPC client for making API calls
        path: API path to fetch items
        request_batch_size: Number of items to fetch per page
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs for images
        is_file_info_required: Whether file info is required
    
    Returns:
        List of dataset items
    """
def fetch_file_info(rpc: Any, dataset_item_id: str, download_images_required: bool = False, page_size: int = 10) -> List[Dict[str, Any]]: ...
    """
    Fetches all file information for a specific dataset item across pages.
    
    Args:
        rpc: RPC client for making API calls
        dataset_item_id: Dataset item identifier
        download_images_required: Whether to get presigned URLs
        page_size: Number of items per page
    
    Returns:
        A list of all file information items
    """
def fetch_items(rpc: Any, path: str, request_batch_size: int, page_number: Optional[int] = None, download_images_required: bool = False) -> List[Dict[str, Any]]: ...
    """
    Fetch items from the dataset API.
    
    Args:
        rpc: RPC client for making API calls
        path: API path to fetch items
        request_batch_size: Number of items to fetch per page
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs for images
    
    Returns:
        List of dataset items
    """
def fetch_video_frame_items(rpc: Any, path: str, request_batch_size: int, page_number: Optional[int] = None, download_images_required: bool = False, is_file_info_required: bool = False) -> List[Dict[str, Any]]: ...
    """
    Fetch video frame items from the dataset API.
    
    Args:
        rpc: RPC client for making API calls
        path: API path to fetch items
        request_batch_size: Number of items to fetch per page
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs for images
        is_file_info_required: Whether file info is required
    
    Returns:
        List of dataset items
    """
def generate_short_uuid() -> str: ...
    """
    Generate a shortened UUID.
    
    Returns:
        Short UUID string
    """
def get_batch_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get a batch of items from a specific dataset version page.
    """
def get_batch_partition_items(rpc: Any, dataset_id: str, partition: int, page_number: int, download_images_required: bool = False, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get a batch of items from a specific partition page.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
    
    Returns:
        List of partition items
    """
def get_batch_pre_signed_download_urls(cloud_file_paths: List[str], rpc: Any, bucket_alias: str = '', account_number: str = '', project_id: Optional[str] = None) -> Dict: ...
    """
    Get batch of pre-signed download URLs.
    
    Args:
        cloud_file_paths: List of cloud file paths
        rpc: RPC client
        bucket_alias: Optional bucket alias
        account_number: Optional account number
    
    Returns:
        Response data or error message
    """
def get_batch_video_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get a batch of items from a specific dataset version page.
    """
def get_classwise_frame_splits(partition_items: List[Dict], annotation_type: str = 'detection', sample_stats: Optional[Dict] = None) -> Tuple[Dict, Dict]: ...
    """
    Get class-wise split statistics for video frames.
    
    Args:
        partition_items: List of partition items
        annotation_type: Type of annotation
        sample_stats: Optional sample statistics
    
    Returns:
        Tuple of class-wise split statistics and unique video statistics
    """
def get_classwise_splits(partition_items: List[Dict], annotation_type: str = 'classification') -> Dict: ...
    """
    Get class-wise split statistics.
    
    Args:
        partition_items: List of partition items
        annotation_type: Type of annotation
    
    Returns:
        Dictionary of class-wise split statistics
    """
def get_corresponding_split_type(path: str, include_year: bool = False) -> str: ...
    """
    Get the split type (train/val/test) from a file path.
    
    Args:
        path: File path to analyze
        include_year: Whether to include year in split type
    
    Returns:
        Split type string
    """
def get_data_prep_batch_video_dataset_items(rpc: Any, dataset_id: str, dataset_version: str, page_number: int, request_batch_size: int = 100, input_type: str = 'davis') -> List[Dict[str, Any]]: ...
    """
    Fetch dataset items and enrich with file info and annotation info.
    """
def get_filename_from_url(url: str) -> str: ...
    """
    Extract filename from URL.
    
    Args:
        url: URL to parse
    
    Returns:
        Extracted filename
    """
def get_number_of_dataset_batches(rpc: Any, dataset_id: str, dataset_version: str, request_batch_size: int = 1) -> int: ...
    """
    Calculate total number of pages for a dataset.
    """
def get_number_of_partition_batches(rpc: Any, dataset_id: str, partition: int, request_batch_size: int = 1) -> int: ...
    """
    Calculate total number of pages for a partition.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        request_batch_size: Number of items per batch
    
    Returns:
        Number of pages
    """
def get_partition_items(rpc: Any, dataset_id: str, partition: int, download_images_required: bool = False, request_batch_size: int = 100) -> List[Dict[str, Any]]: ...
    """
    Get all items for a partition.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
    
    Returns:
        List of all partition items
    """
def get_unprocessed_partitions(rpc: Any, dataset_id: str, version: str) -> List[int]: ...
    """
    Get list of unprocessed partition numbers.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        version: Dataset version
    
    Returns:
        List of unprocessed partition numbers
    """
def get_video_frame_batch_partition_items(rpc: Any, dataset_id: str, partition: int, page_number: int, download_images_required: bool = False, request_batch_size: int = 100, is_file_info_required: bool = False, input_type: str = 'mscoco_video') -> List[Dict[str, Any]]: ...
    """
    Get a batch of video frame items from a specific partition page.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        page_number: Page number to fetch
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
        is_file_info_required: Whether file info is required
    
    Returns:
        List of partition items with added file info and presigned URLs if requested
    """
def get_video_frame_partition_items(rpc: Any, dataset_id: str, partition: int, download_images_required: bool = False, request_batch_size: int = 100, is_file_info_required: bool = True, input_type: str = 'mscoco_video') -> List[Dict[str, Any]]: ...
    """
    Get all video frame items for a partition.
    
    Args:
        rpc: RPC client
        dataset_id: Dataset identifier
        partition: Partition number
        download_images_required: Whether to get presigned URLs
        request_batch_size: Number of items per batch
        is_file_info_required: Whether file info is required
    
    Returns:
        List of all partition items
    """
def handle_source_url_dataset_download(source_url: Any) -> str: ...
    """
    Handle dataset download from source URL.
    """
def log_error(action_record_id: str, exception: Any, filename: str, function_name: str, rpc: Any) -> None: ...
    """
    Log error to system.
    
    Args:
        action_record_id: Action record identifier
        exception: Exception that occurred
        filename: Name of file where error occurred
        function_name: Name of function where error occurred
        rpc: RPC client
    """
def paginate_all(rpc: Any, path_template: str) -> List[Dict[str, Any]]: ...
def rpc_get_call(rpc: Any, path: str, params: Optional[Dict] = None) -> Optional[Dict]: ...
    """
    Make RPC GET call.
    
    Args:
        rpc: RPC client
        path: API path
        params: Optional query parameters
    
    Returns:
        Response data or None on failure
    """
def update_action_status(action_record_id: str, action_type: str, step_code: str, status: str, status_description: str, rpc: Any) -> None: ...
    """
    Update action status.
    
    Args:
        action_record_id: Action record identifier
        action_type: Type of action
        step_code: Code for current step
        status: Status to set
        status_description: Description of status
        rpc: RPC client
    """
def update_partition_status(rpc: Any, action_record_id: str, dataset_id: str, version: str, partition: int, status: str, partition_items: List[Dict], annotation_type: str) -> Optional[Dict]: ...
    """
    Update partition processing status.
    
    Args:
        rpc: RPC client
        action_record_id: Action record identifier
        dataset_id: Dataset identifier
        version: Dataset version
        partition: Partition number
        status: Status to set
        partition_items: Items in partition
        annotation_type: Type of annotation
    
    Returns:
        Response data or None on failure
    
    Raises:
        Exception: If update fails
    """
def update_video_frame_partition_status(rpc: Any, action_record_id: str, dataset_id: str, version: str, partition: int, status: str, partition_items: List[Dict], annotation_type: str, sample_stats: Optional[Dict] = None) -> Optional[Dict]: ...
    """
    Update video frame partition processing status.
    
    Args:
        rpc: RPC client
        action_record_id: Action record identifier
        dataset_id: Dataset identifier
        version: Dataset version
        partition: Partition number
        status: Status to set
        partition_items: Items in partition
        annotation_type: Type of annotation
        sample_stats: Optional sample statistics
    
    Returns:
        Response data or None on failure
    
    Raises:
        Exception: If update fails
    """
