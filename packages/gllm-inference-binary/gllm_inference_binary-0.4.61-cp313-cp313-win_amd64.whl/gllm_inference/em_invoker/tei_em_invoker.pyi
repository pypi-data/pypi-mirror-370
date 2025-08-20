from _typeshed import Incomplete
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker as BaseEMInvoker
from gllm_inference.em_invoker.langchain import TEIEmbeddings as TEIEmbeddings
from gllm_inference.schema import ModelId as ModelId, ModelProvider as ModelProvider, Vector as Vector
from gllm_inference.utils import get_basic_auth_headers as get_basic_auth_headers, preprocess_tei_input as preprocess_tei_input

DEPRECATION_MESSAGE: str

class TEIEMInvoker(BaseEMInvoker):
    """An embedding model invoker to interact with embedding models hosted in Text Embeddings Inference (TEI).

    The `TEIEMInvoker` class is responsible for invoking an embedding model in Text Embeddings Inference (TEI).
    It uses the embedding model to transform a text or a list of input text into their vector representations.

    Attributes:
        model_id (str): The model ID of the embedding model.
        model_provider (str): The provider of the embedding model.
        model_name (str): The name of the embedding model.
        client (AsyncInferenceClient): The client instance to interact with the TEI service.
        query_prefix (str): The additional prefix to be added when embedding a query.
        document_prefix (str): The additional prefix to be added when embedding documents.
        retry_config (RetryConfig): The retry configuration for the embedding model.
    """
    client: Incomplete
    query_prefix: Incomplete
    document_prefix: Incomplete
    def __init__(self, url: str, username: str = '', password: str = '', api_key: str | None = None, query_prefix: str = '', document_prefix: str = '', retry_config: RetryConfig | None = None) -> None:
        """Initializes a new instance of the TEIEMInvoker class.

        Args:
            url (str): The URL of the TEI service.
            username (str, optional): The username for Basic Authentication. Defaults to an empty string.
            password (str, optional): The password for Basic Authentication. Defaults to an empty string.
            api_key (str | None, optional): The API key for the TEI service. Defaults to None.
            query_prefix (str, optional): The additional prefix to be added when embedding a query.
                Defaults to an empty string.
            document_prefix (str, optional): The additional prefix to be added when embedding documents.
                Defaults to an empty string.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout is used.
        """
    def to_langchain(self) -> TEIEmbeddings:
        """Converts the current embedding model invoker to an instance of LangChain `TEIEmbeddings` object.

        Returns:
            TEIEmbeddings: An instance of LangChain `TEIEmbeddings` object.
        """
