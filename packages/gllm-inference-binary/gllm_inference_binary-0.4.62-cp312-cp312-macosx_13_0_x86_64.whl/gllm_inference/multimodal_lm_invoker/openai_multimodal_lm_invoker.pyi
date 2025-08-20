from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.multimodal_lm_invoker.multimodal_lm_invoker import BaseMultimodalLMInvoker as BaseMultimodalLMInvoker
from gllm_inference.utils import get_mime_type as get_mime_type, is_local_file_path as is_local_file_path, is_remote_file_path as is_remote_file_path
from gllm_inference.utils.openai_multimodal_lm_helper import parse_prompt as parse_prompt, validate_content_type as validate_content_type
from typing import Any

VALID_EXTENSIONS: Incomplete
DEPRECATION_MESSAGE: str

class OpenAIMultimodalLMInvoker(BaseMultimodalLMInvoker[str | bytes, str]):
    """An invoker to interact with multimodal language models hosted through OpenAI API endpoints.

    The `OpenAIMultimodalLMInvoker` class is designed to interact with multimodal language models hosted through
    OpenAI API endpoints. It provides a framework for invoking multimodal language models with the provided prompt and
    hyperparameters. It supports both standard and streaming invocation. Streaming mode is enabled if an event emitter
    is provided.

    Attributes:
        client (AsyncOpenAI): The AsyncOpenAI client instance.
        model_name (str): The name of the OpenAI model.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the multimodal language model.

    Notes:
        The `OpenAIMultimodalLMInvoker` currently supports the following contents:
        1. Text, which can be passed as plain strings.
        2. Image, which can be passed as:
           1. Base64 encoded image bytes.
           2. URL pointing to an image.
           3. Local image file path.
    """
    client: Incomplete
    model_name: Incomplete
    def __init__(self, model_name: str, api_key: str, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the OpenAIMultimodalLMInvoker class.

        Args:
            model_name (str): The name of the OpenAI model.
            api_key (str): The API key for authenticating with OpenAI.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
        """
