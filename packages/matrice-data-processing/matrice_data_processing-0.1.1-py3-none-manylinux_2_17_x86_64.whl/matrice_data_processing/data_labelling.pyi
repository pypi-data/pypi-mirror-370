"""Auto-generated stub for module: data_labelling."""
from typing import Any, Dict, List, Optional, Union

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from matrice.projects import Projects
from matrice_data_processing.data_prep import dataset_items_producer, get_item_set_type
from matrice_data_processing.pipeline import Pipeline
from matrice_data_processing.server import batch_update_dataset_items
from matrice_data_processing.server_utils import generate_short_uuid, get_number_of_dataset_batches
from matrice_inference.deploy.client import MatriceDeployClient
from matrice_inference.deployment import Deployment
from queue import Queue
import logging
import os
import time

# Functions
def add_dataset_item_annotations(dataset_item: Dict, prediction_result: Dict, project_type: str) -> Dict: ...
    """
    Add annotations to dataset item based on prediction results
    
        Args:
            dataset_item: Dataset item to annotate
            prediction_result: Prediction results
            project_type: Type of project (classification/detection/instance_segmentation)
    
        Returns:
            Dict: Annotated dataset item
    
        Raises:
            Exception: If annotation fails
    """
def convert_to_mscoco_format(x_min: float, y_min: float, x_max: float, y_max: float) -> List[float]: ...
    """
    Convert bounding box coordinates to MSCOCO format.
    
        Args:
            x_min: Minimum x coordinate
            y_min: Minimum y coordinate
            x_max: Maximum x coordinate
            y_max: Maximum y coordinate
    
        Returns:
            List[float]: [x_min, y_min, width, height]
    """
def create_model_deployment_client(session: Any, project_type: str, project_id: str, model_id: str = '', model_type: str = 'pretrained', deployment_type: str = 'regular', checkpoint_type: str = 'pretrained', checkpoint_value: str = '', suggested_classes: List[str] = [], compute_alias: str = '', runtime_framework: str = 'Pytorch', model_family: str = '', model_key: str = '') -> Union[MatriceDeployClient, Deployment]: ...
    """
    Create and test a model deployment
    
        Args:
            session: Session object
            project_type: Type of project
            project_id: ID of project
            model_id: ID of model
            model_type: Type of model
            deployment_type: Type of deployment
            checkpoint_type: Type of checkpoint
            checkpoint_value: Value of checkpoint
            suggested_classes: List of suggested classes
            compute_alias: Compute alias
            runtime_framework: Runtime framework
            model_family: Model family name
            model_key: Model key identifier
    
        Returns:
            MatriceDeployClient: Deployment client if successful
    
        Raises:
            Exception: If deployment fails
    """
def get_dataset_labelling_pipeline(session: Any, dataset_id: str, dataset_version: str, deploy_client: Any, project_type: str) -> Any: ...
    """
    Create dataset labeling pipeline
    
        Args:
            session: Session object
            dataset_id: ID of dataset
            dataset_version: Version of dataset
            deploy_client: Deployment client for predictions
            project_type: Type of project
    
        Returns:
            Pipeline: Configured pipeline object
    
        Raises:
            Exception: If pipeline creation fails
    """
def label_dataset_items(batch_dataset_items: List[Dict], deploy_client: Union[MatriceDeployClient, Deployment], project_type: str, dataset_version: str) -> List[Dict]: ...
    """
    Label batch of dataset items using model predictions
    
        Args:
            batch_dataset_items: List of dataset items to label
            deploy_client: Deployment client
            project_type: Type of project
            dataset_version: Version of dataset
    
        Returns:
            List[Dict]: Labeled dataset items
    
        Raises:
            Exception: If labeling fails
    """
def test_model_prediction(session: Any, deployment_class: Any, max_tries: int = 5, initial_wait: int = 180, retry_wait: int = 180) -> Union[MatriceDeployClient, Deployment]: ...
    """
    Test model prediction with retries
    
        Args:
            session: Session object
            deployment_class: Model deployment object
            max_tries: Maximum number of prediction attempts
            initial_wait: Initial wait time in seconds
            retry_wait: Wait time between retries in seconds
    
        Returns:
            Optional[MatriceDeployClient]: Deploy client if successful, None otherwise
    """
def update_dataset_items_keys(dataset_items: List[Dict], dataset_version: str) -> List[Dict]: ...
    """
    Update dataset items keys
    
        Args:
            dataset_items: List of dataset items
            dataset_version: Version of dataset
    
        Returns:
            List[Dict]: Updated dataset items
    """

# Classes
class DataLabelling:
    """
    Class to handle dataset labelling.
    """

    def __init__(self: Any, session: Any, action_record_id: str) -> None: ...
        """
        Initialize DataLabelling.
        
                Args:
                    session: Session object with RPC client
                    action_record_id: ID of action record
        
                Raises:
                    Exception: If initialization fails
        """

    def create_model_deployment(self: Any) -> Any: ...
        """
        Create model deployment
        
                Returns:
                    MatriceDeployClient: Deployment client
        
                Raises:
                    Exception: If deployment creation fails
        """

    def mark_dataset_as_labelled(self: Any) -> None: ...
        """
        Mark dataset as labelled
        
                Raises:
                    Exception: If marking dataset as labelled fails
        """

    def start_processing(self: Any) -> None: ...
        """
        Start dataset labelling processing.
        
                Raises:
                    Exception: If processing fails
        """

    def update_status(self: Any, stepCode: str, status: str, status_description: str, sample_count: int = None) -> None: ...
        """
        Update status of data labelling.
        
                Args:
                    stepCode: Code indicating current step
                    status: Status of step
                    status_description: Description of status
        
                Raises:
                    Exception: If status update fails
        """

