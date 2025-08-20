from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.lm_invoker.google_lm_invoker import GoogleLMInvoker as GoogleLMInvoker
from gllm_inference.schema import ResponseSchema as ResponseSchema
from langchain_core.tools import Tool as Tool
from typing import Any

DEPRECATION_MESSAGE: str

class GoogleGenerativeAILMInvoker(GoogleLMInvoker):
    """A language model invoker to interact with Google Gen AI language models.

    This class has been deprecated as Google Generative AI is now supported through `GoogleLMInvoker`.
    This class is maintained for backward compatibility and will be removed in version 0.5.0.

    Attributes:
        model_id (str): The model ID of the language model.
        model_provider (str): The provider of the language model.
        model_name (str): The name of the language model.
        client (Client): The Google client instance.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Any]): The list of tools provided to the model to enable tool calling.
        response_schema (ResponseSchema | None): The schema of the response. If provided, the model will output a
            structured response as defined by the schema. Supports both Pydantic BaseModel and JSON schema dictionary.
        output_analytics (bool): Whether to output the invocation analytics.
        retry_config (RetryConfig | None): The retry configuration for the language model.
    """
    def __init__(self, model_name: str, api_key: str, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, tools: list[Tool] | None = None, response_schema: ResponseSchema | None = None, output_analytics: bool = False, retry_config: RetryConfig | None = None, bind_tools_params: dict[str, Any] | None = None, with_structured_output_params: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the GoogleGenerativeAILMInvoker class.

        Args:
            model_name (str): The name of the multimodal language model to be used.
            api_key (str): The API key for authenticating with Google Gen AI.
            model_kwargs (dict[str, Any] | None, optional): Additional keyword arguments for the Google Generative AI
                client.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            tools (list[Tool] | None, optional): Tools provided to the language model to enable tool calling.
                Defaults to None.
            response_schema (ResponseSchema | None, optional): The schema of the response. If provided, the model will
                output a structured response as defined by the schema. Supports both Pydantic BaseModel and JSON schema
                dictionary. Defaults to None.
            output_analytics (bool, optional): Whether to output the invocation analytics. Defaults to False.
            retry_config (RetryConfig | None, optional): The retry configuration for the language model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout is used.
            bind_tools_params (dict[str, Any] | None, optional): Deprecated parameter to add tool calling capability.
                If provided, must at least include the `tools` key that is equivalent to the `tools` parameter.
                Retained for backward compatibility. Defaults to None.
            with_structured_output_params (dict[str, Any] | None, optional): Deprecated parameter to instruct the
                model to produce output with a certain schema. If provided, must at least include the `schema` key that
                is equivalent to the `response_schema` parameter. Retained for backward compatibility. Defaults to None.
        """
