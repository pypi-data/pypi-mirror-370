"""Auto-generated stub for module: data_processor."""
from typing import Any

from matrice_data_processing.client import handle_client_processing_pipelines, handle_client_video_processing_pipelines
from matrice_data_processing.pipeline import Pipeline
from matrice_data_processing.server import get_mscoco_server_processing_pipeline, get_imagenet_server_processing_pipeline, get_pascalvoc_server_processing_pipeline, get_labelbox_server_processing_pipeline, get_yolo_server_processing_pipeline, get_unlabelled_server_processing_pipeline, get_labelbox_classification_server_processing_pipeline, handle_source_url_dataset_download, download_labelbox_dataset, get_video_youtube_bb_tracking_server_processing_pipeline, get_video_mot_tracking_server_processing_pipeline, get_video_davis_segmentation_server_processing_pipeline, get_video_imagenet_classification_server_processing_pipeline, get_kinetics_server_processing_pipeline, get_video_mscoco_server_processing_pipeline
from matrice_data_processing.server_utils import get_number_of_dataset_batches
import logging

# Classes
class DataProcessor:
    """
    Class for processing data through various pipelines.
    """

    def __init__(self: Any, session: Any, action_record_id: Any) -> None: ...
        """
        Initialize DataProcessor with session and action record ID.
        """

    def get_server_processing_pipeline(self: Any) -> Any: ...
        """
        Get the appropriate server processing pipeline based on input type.
        """

    def start_processing(self: Any) -> Any: ...
        """
        Start the data processing pipeline.
        """

    def update_status(self: Any, step_code: Any, status: Any, status_description: Any, sample_count: Any = None) -> None: ...
        """
        Update the status of the data processing job.
        """

