"""Auto-generated stub for module: create_dataset."""
from typing import Any

from matrice.dataset import Dataset
from matrice.dataset import get_dataset_size_in_mb_from_url
from matrice_data_processing.client import handle_client_processing_pipelines, handle_client_video_processing_pipelines, get_partition_status, get_video_partition_status
from matrice_data_processing.client_utils import get_size_mb, upload_compressed_dataset, is_file_compressed, complete_dataset_items_upload, get_youtube_bb_partitions, get_mot_partitions, get_davis_partitions, get_video_imagenet_partitions, get_kinetics_partitions, get_video_mscoco_partitions, extract_frames_from_videos, scan_dataset
import logging

# Functions
def create_dataset(session: Any, project_id: Any, account_number: Any, dataset_name: Any, project_type: Any = 'detection', dataset_type: Any = 'detection', input_type: Any = 'MSCOCO', dataset_path: Any = '', source_url: Any = '', url_type: Any = '', bucket_alias: Any = '', compute_alias: Any = '', target_cloud_storage: Any = '', source_credential_alias: Any = '', bucket_alias_service_provider: Any = 'auto') -> Any: ...
    """
    Create a new dataset.
    
    Parameters
    ----------
    session : Session
        The session object used for API interactions.
    project_id : str
        The ID of the project.
    account_number : str
        The account number associated with the session.
    project_type : str
        The type of project.
    dataset_name : str
        The name of the dataset.
    dataset_type : str, optional
        The type of dataset (default is "detection")
    input_type : str, optional
        The input type for the dataset (default is "MSCOCO")
    dataset_path : str, optional
        Local path to dataset files (default is "")
    source_url : str, optional
        URL to dataset source (default is "")
    url_type : str, optional
        Type of URL source (default is "")
    bucket_alias : str, optional
        Alias for cloud storage bucket (default is "")
    compute_alias : str, optional
        Alias for compute resources (default is "")
    target_cloud_storage : str, optional
        Target cloud storage location (default is "")
    source_credential_alias : str, optional
        Alias for source credentials (default is "")
    bucket_alias_service_provider : str, optional
        Service provider for bucket alias (default is "auto")
    
    Returns
    -------
    Dataset
        A Dataset object for the created dataset.
    
    Example
    -------
    >>> dataset = project._create_dataset(
    ...     dataset_name="MyDataset",
    ...     dataset_path="/path/to/data",
    ...     dataset_type="detection"
    ... )
    >>> print(f"Dataset created: {dataset}")
    """
