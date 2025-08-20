from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.em_invoker.google_em_invoker import GoogleEMInvoker as GoogleEMInvoker
from typing import Any

DEPRECATION_MESSAGE: str

class GoogleGenerativeAIEMInvoker(GoogleEMInvoker):
    """An embedding model invoker to interact with Google Generative AI embedding models.

    This class has been deprecated as Google Generative AI is now supported through `GoogleEMInvoker`.
    This class is maintained for backward compatibility and will be removed in version 0.5.0.

    Attributes:
        model_id (str): The model ID of the embedding model.
        model_provider (str): The provider of the embedding model.
        model_name (str): The name of the embedding model.
        client_params (dict[str, Any]): The Google client instance init parameters.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the embedding model.
        retry_config (RetryConfig | None): The retry configuration for the language model.
    """
    def __init__(self, model_name: str, api_key: str, task_type: str | None = None, model_kwargs: Any = None, retry_config: RetryConfig | None = None) -> None:
        """Initializes a new instance of the GoogleGenerativeAIEMInvoker class.

        Args:
            model_name (str): The name of the Google Generative AI model to be used.
            api_key (str): The API key for accessing the Google Generative AI model.
            task_type (str | None, optional): The type of task to be performed by the embedding model. Defaults to None.
            model_kwargs (Any, optional): Additional keyword arguments to initiate the embedding model.
                Defaults to None.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout is used.
        """
