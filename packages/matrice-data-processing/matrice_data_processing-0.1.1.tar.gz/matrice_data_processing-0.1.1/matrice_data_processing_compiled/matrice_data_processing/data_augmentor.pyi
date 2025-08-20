"""Auto-generated stub for module: data_augmentor."""
from typing import Any, Dict

from image_data_augmentation import create_probability_based_augmentation_pipeline, parse_dynamic_pipeline_config, DynamicPipelineConfig, AugmentationStep
import json
import logging
import os
import sys
import traceback
import traceback

# Functions
def create_completion_api_config() -> str: ...
    """
    Create completion API URL configuration
    """
def create_kafka_config() -> Dict[str, Any]: ...
    """
    Create Kafka configuration with hardcoded values
    """
def create_sample_pipeline_config() -> Dict[str, Any]: ...
    """
    Create a sample pipeline configuration for testing
    """
def initialize_and_run_pipeline() -> Any: ...
    """
    Initialize and run the probability-based augmentation pipeline
    """
def run_with_custom_config(config_file_path: str = None) -> Any: ...
    """
    Run pipeline with custom configuration from file
    """
def transform_augmentation_data(input_dict: Any) -> Any: ...
    """
    Transform input augmentation dictionary into a list of output dictionaries,
    one for each augmentation chain.
    """

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

