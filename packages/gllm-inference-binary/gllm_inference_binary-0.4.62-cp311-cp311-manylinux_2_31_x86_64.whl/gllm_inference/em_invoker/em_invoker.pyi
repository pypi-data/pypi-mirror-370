import abc
from _typeshed import Incomplete
from abc import ABC
from gllm_core.utils.retry import RetryConfig
from gllm_inference.constants import ALL_EXTENSIONS as ALL_EXTENSIONS, DOCUMENT_MIME_TYPES as DOCUMENT_MIME_TYPES
from gllm_inference.exceptions import parse_error_message as parse_error_message
from gllm_inference.schema import Attachment as Attachment, AttachmentType as AttachmentType, EMContent as EMContent, ModelId as ModelId, Vector as Vector
from langchain_core.embeddings import Embeddings as Embeddings
from typing import Any

DEPRECATED_DETAILS: str

class BaseEMInvoker(ABC, metaclass=abc.ABCMeta):
    """A base class for embedding model invokers used in Gen AI applications.

    The `BaseEMInvoker` class provides a framework for invoking embedding models.

    Attributes:
        model_id (str): The model ID of the embedding model.
        model_provider (str): The provider of the embedding model.
        model_name (str): The name of the embedding model.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the embedding model.
        retry_config (RetryConfig): The retry configuration for the embedding model.
    """
    default_hyperparameters: Incomplete
    retry_config: Incomplete
    def __init__(self, model_id: ModelId, default_hyperparameters: dict[str, Any] | None = None, valid_extensions_map: dict[str, set[str]] | None = None, retry_config: RetryConfig | None = None, langchain_kwargs: dict[str, Any] | None = None) -> None:
        '''Initializes a new instance of the BaseEMInvoker class.

        Args:
            model_id (ModelId): The model ID of the embedding model.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the
                embedding model. Defaults to None, in which case an empty dictionary is used.
            valid_extensions_map (dict[str, set[str]] | None, optional): A dictionary mapping for validating the
                content type of the multimodal inputs. They keys are the mime types (e.g. "image") and the values are
                the set of valid file extensions for the corresponding mime type. Defaults to None, in which case an
                empty dictionary is used.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout is used.
            langchain_kwargs (dict[str, Any] | None, optional): Additional keyword arguments to initiate the LangChain
                embedding model. Defaults to None.
        '''
    @property
    def model_id(self) -> str:
        """The model ID of the embedding model.

        Returns:
            str: The model ID of the embedding model.
        """
    @property
    def model_provider(self) -> str:
        """The provider of the embedding model.

        Returns:
            str: The provider of the embedding model.
        """
    @property
    def model_name(self) -> str:
        """The name of the embedding model.

        Returns:
            str: The name of the embedding model.
        """
    async def invoke(self, content: EMContent | list[EMContent], hyperparameters: dict[str, Any] | None = None) -> Vector | list[Vector]:
        """Invokes the embedding model with the provided content or list of contents.

        This method invokes the embedding model with the provided content or list of contents.
        It includes retry logic with exponential backoff for transient failures.

        Args:
            content (EMContent | list[EMContent]): The input or list of inputs to be embedded using the embedding model.
            hyperparameters (dict[str, Any] | None, optional): A dictionary of hyperparameters for the embedding model.
                Defaults to None, in which case the default hyperparameters are used.

        Returns:
            Vector | list[Vector]: The vector representations of the input contents:
                1. If the input is an `EMContent`, the output is a `Vector`.
                2. If the input is a `list[EMContent]`, the output is a `list[Vector]`.

        Raises:
            CancelledError: If the invocation is cancelled.
            ModelNotFoundError: If the model is not found.
            ProviderAuthError: If the model authentication fails.
            ProviderInternalError: If the model internal error occurs.
            ProviderInvalidArgsError: If the model parameters are invalid.
            ProviderOverloadedError: If the model is overloaded.
            ProviderRateLimitError: If the model rate limit is exceeded.
            TimeoutError: If the invocation times out.
            ValueError: If the input content is invalid.
        """
    def to_langchain(self) -> Embeddings:
        """Converts the current embedding model invoker to an instance of LangChain `Embeddings` object.

        This method converts the EM invoker to an instance of LangChain's `Embeddings` object.
        This method requires the appropriate `langchain-<provider>` package to be installed.

        Returns:
            Embeddings: An instance of LangChain `Embeddings` object.

        Raises:
            ValueError: If `langchain_module_name` or `langchain_class_name` is missing.
        """
