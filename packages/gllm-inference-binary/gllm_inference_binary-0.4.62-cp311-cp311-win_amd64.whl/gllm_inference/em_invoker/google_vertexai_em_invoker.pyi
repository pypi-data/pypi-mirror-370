from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.em_invoker.google_em_invoker import GoogleEMInvoker as GoogleEMInvoker
from typing import Any

DEPRECATION_MESSAGE: str

class GoogleVertexAIEMInvoker(GoogleEMInvoker):
    """An embedding model invoker to interact with Google Vertex AI embedding models.

    This class has been deprecated as Google Vertex AI is now supported through `GoogleEMInvoker`.
    This class is maintained for backward compatibility and will be removed in version 0.5.0.

    Attributes:
        model_id (str): The model ID of the embedding model.
        model_provider (str): The provider of the embedding model.
        model_name (str): The name of the embedding model.
        client_params (dict[str, Any]): The Google client instance init parameters.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the embedding model.
        retry_config (RetryConfig | None): The retry configuration for the language model.
    """
    def __init__(self, model_name: str, credentials_path: str, project_id: str | None = None, location: str = 'us-central1', model_kwargs: Any = None, retry_config: RetryConfig | None = None) -> None:
        '''Initializes a new instance of the GoogleVertexAIEMInvoker class.

        Args:
            model_name (str): The name of the multimodal embedding model to be used.
            credentials_path (str): The path to the Google Cloud service account credentials JSON file.
            project_id (str | None, optional): The Google Cloud project ID. Defaults to None, in which case the
                project ID will be loaded from the credentials file.
            location (str, optional): The location of the Google Cloud project. Defaults to "us-central1".
            model_kwargs (Any, optional): Additional keyword arguments to initiate the Google Vertex AI model.
                Defaults to None.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout is used.
        '''
