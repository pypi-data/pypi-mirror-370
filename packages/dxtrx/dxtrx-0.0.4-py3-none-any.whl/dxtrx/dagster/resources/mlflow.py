import mlflow
import dagster as dg

from datetime import datetime
from pydantic import BaseModel

class MLflowModelLoadResult(BaseModel):
    """
    Represents the result of loading a model from MLflow.
    
    Attributes:
        model: The loaded model object
        model_uri: The URI used to load the model
        load_timestamp: When the model was loaded
        model_details: Additional metadata about the loaded model
    """
    model: object
    model_uri: str
    load_timestamp: datetime
    model_details: dict

class MLflowResource(dg.ConfigurableResource):
    """
    A resource for interacting with MLflow tracking server.
    
    Attributes:
        tracking_uri: The MLflow tracking server URI
    """
    tracking_uri: str

    def setup_for_execution(self, context: dg.InitResourceContext):
        """Initialize the MLflow resource with logging."""
        self._logger = dg.get_dagster_logger()
        
        # TODO: This will not be a problem with one MLflow server per Dagster instance, 
        # but it will be a problem if trying to use multiple MLflow servers. 
        # Hopefully this will not be an issue for now nor in the future.
        mlflow.set_tracking_uri(self.tracking_uri) 
        self._logger.info(f"MLflow tracking URI set to: {self.tracking_uri}")
        
        self._mlflow_client = mlflow.client.MlflowClient(self.tracking_uri)
        
    def load_model_by_name_and_tag(self, model_name: str, model_tag: str) -> MLflowModelLoadResult:
        """
        Load a model from MLflow using its name and tag.
        
        Args:
            model_name: Name of the model in MLflow
            model_tag: Tag to identify the model version
            
        Returns:
            MLflowModelLoadResult: Information about the loaded model
            
        Raises:
            Exception: If model loading fails
        """
        model_uri = f"models:/{model_name}@{model_tag}"
        return self._load_model(model_uri, {
            "model_name": model_name,
            "model_tag": model_tag
        })
        
    def get_client(self):
        """
        Get the MLflow client.
        """
        return self._mlflow_client

    def load_model_by_uri(self, model_uri: str) -> MLflowModelLoadResult:
        """
        Load a model from MLflow using its direct URI.
        
        Args:
            model_uri: Direct URI to the model
            
        Returns:
            MLflowModelLoadResult: Information about the loaded model
            
        Raises:
            Exception: If model loading fails
        """
        return self._load_model(model_uri, {
            "model_uri": model_uri
        })

    def _load_model(self, model_uri: str, model_details: dict) -> MLflowModelLoadResult:
        """
        Internal method to load a model from MLflow.
        
        Args:
            model_uri: URI to load the model from
            model_details: Additional metadata about the model
            
        Returns:
            MLflowModelLoadResult: Information about the loaded model
            
        Raises:
            Exception: If model loading fails
        """
        try:
            self._logger.info(f"🔄 Loading model from MLflow: {model_uri}")
            model = mlflow.pyfunc.load_model(model_uri)
            self._logger.info("✅ Model loaded successfully")
            
            return MLflowModelLoadResult(
                model=model,
                model_uri=model_uri,
                load_timestamp=datetime.now(),
                model_details=model_details
            )
            
        except Exception as e:
            self._logger.error(f"❌ Failed to load model: {str(e)}")
            raise Exception(f"Failed to load model from MLflow: {str(e)}")
