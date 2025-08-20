from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.lm_invoker import GoogleLMInvoker as GoogleLMInvoker
from gllm_inference.multimodal_lm_invoker.multimodal_lm_invoker import BaseMultimodalLMInvoker as BaseMultimodalLMInvoker
from pydantic import BaseModel as BaseModel
from typing import Any

DEPRECATION_MESSAGE: str

class GoogleGenerativeAIMultimodalLMInvoker(BaseMultimodalLMInvoker[str | bytes, str]):
    """An invoker to interact with multimodal language models hosted through Google's Generative AI API endpoints.

    This class is deprecated as it has been replaced by the `GoogleLMInvoker` class.

    Attributes:
        model (GoogleLMInvoker): The Google Gemini model instance.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the multimodal language model.
    """
    model: Incomplete
    def __init__(self, model_name: str, api_key: str, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, response_schema: BaseModel | None = None) -> None:
        """Initializes a new instance of the GoogleGenerativeAIMultimodalLMInvoker class.

        Args:
            model_name (str): The name of the Google Gemini model.
            api_key (str): The API key for authenticating with Google Gemini.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            response_schema (BaseModel | None, optional): The response schema for the model. Defaults to None.
        """
