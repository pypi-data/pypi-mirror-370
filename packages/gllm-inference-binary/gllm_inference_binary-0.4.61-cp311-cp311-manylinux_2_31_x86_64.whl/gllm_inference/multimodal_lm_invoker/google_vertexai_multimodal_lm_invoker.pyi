from _typeshed import Incomplete
from enum import Enum as Enum
from gllm_core.constants import EventLevel as EventLevel, EventType as EventType
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.multimodal_lm_invoker.multimodal_lm_invoker import BaseMultimodalLMInvoker as BaseMultimodalLMInvoker
from gllm_inference.schema import PromptRole as PromptRole
from gllm_inference.utils import get_mime_type as get_mime_type, invoke_google_multimodal_lm as invoke_google_multimodal_lm, is_local_file_path as is_local_file_path, is_remote_file_path as is_remote_file_path, load_google_vertexai_project_id as load_google_vertexai_project_id
from pydantic import BaseModel as BaseModel
from typing import Any

VALID_EXTENSION_MAP: Incomplete
VALID_EXTENSIONS: Incomplete
DEPRECATION_MESSAGE: str

class GoogleVertexAIMultimodalLMInvoker(BaseMultimodalLMInvoker[str | bytes, str]):
    """An invoker to interact with multimodal language models hosted through Google's Vertex AI API endpoints.

    The `GoogleVertexAIMultimodalLMInvoker` class is designed to interact with multimodal language models hosted
    through Google's Vertex AI API endpoints. It provides a framework for invoking multimodal language models with
    the provided prompt and hyperparameters. It supports both standard and streaming invocation. Streaming mode is
    enabled if an event emitter is provided.

    Attributes:
        client (GenerativeModel): The Google Vertex AI client instance.
        extra_kwargs (dict[str, Any]): Additional keyword arguments for the `generate_content_async` method.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the multimodal language model.

    Notes:
        The `GoogleVertexAIMultimodalLMInvoker` currently supports the following contents:
        1. Text, which can be passed as plain strings.
        2. Audio, which can be passed as:
            1. Base64 encoded audio bytes.
            2. URL pointing to an audio file.
            3. Local audio file path.
        3. Image, which can be passed as:
            1. Base64 encoded image bytes.
            2. URL pointing to an image.
            3. Local image file path.
        4. Video, which can be passed as:
            1. Base64 encoded video bytes.
            2. URL pointing to a video.
            3. Local video file path.
        5. Document, which can be passed as:
            1. Base64 encoded document bytes.
            2. URL pointing to a document.
            3. Local document file path.

        The `GoogleVertexAIMultimodalLMInvoker` also supports structured outputs through the `response_schema`
        argument. For more information, please refer to the following page:
        https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output.
    """
    client: Incomplete
    extra_kwargs: Incomplete
    def __init__(self, model_name: str, credentials_path: str, project_id: str | None = None, location: str = 'us-central1', model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, response_schema: dict[str, Any] | None = None) -> None:
        '''Initializes a new instance of the GoogleVertexAIMultimodalLMInvoker class.

        Args:
            model_name (str): The name of the multimodal language model to be used.
            credentials_path (str): The path to the Google Cloud service account credentials JSON file.
            project_id (str | None, optional): The Google Cloud project ID. Defaults to None, in which case the
                project ID will be loaded from the credentials file.
            location (str, optional): The location of the Google Cloud project. Defaults to "us-central1".
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            response_schema (dict[str, Any] | None, optional): The response schema for the model. Defaults to None.
        '''
