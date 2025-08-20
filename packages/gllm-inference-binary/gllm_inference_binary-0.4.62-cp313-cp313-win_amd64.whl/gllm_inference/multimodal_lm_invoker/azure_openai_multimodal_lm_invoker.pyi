from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.multimodal_lm_invoker.multimodal_lm_invoker import BaseMultimodalLMInvoker as BaseMultimodalLMInvoker
from gllm_inference.utils.openai_multimodal_lm_helper import parse_prompt as parse_prompt, validate_content_type as validate_content_type
from typing import Any

DEPRECATION_MESSAGE: str

class AzureOpenAIMultimodalLMInvoker(BaseMultimodalLMInvoker[str | bytes, str]):
    """An invoker to interact with multimodal language models hosted through Azure OpenAI API endpoints.

    The `AzureOpenAIMultimodalLMInvoker` class is designed to interact with multimodal language models hosted through
    Azure OpenAI API endpoints. It provides a framework for invoking multimodal language models with the provided prompt
    and hyperparameters. It supports both standard and streaming invocation.
    Streaming mode is enabled if an event emitter is provided.

    Attributes:
        client (AsyncAzureOpenAI): The AsyncAzureOpenAI client instance.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the multimodal language model.

    Notes:
        The `AzureOpenAIMultimodalLMInvoker` currently supports the following contents:
        1. Text, which can be passed as plain strings.
        2. Image, which can be passed as:
           1. Base64 encoded image bytes.
           2. URL pointing to an image.
           3. Local image file path.
    """
    client: Incomplete
    def __init__(self, api_key: str, azure_endpoint: str, azure_deployment: str, api_version: str, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the AzureOpenAIMultimodalLMInvoker class.

        Args:
            api_key (str): The API key for authenticating with Azure OpenAI.
            azure_endpoint (str): The endpoint of the Azure OpenAI service.
            azure_deployment (str): The deployment of the Azure OpenAI service.
            api_version (str): The API version of the Azure OpenAI service.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
        """
