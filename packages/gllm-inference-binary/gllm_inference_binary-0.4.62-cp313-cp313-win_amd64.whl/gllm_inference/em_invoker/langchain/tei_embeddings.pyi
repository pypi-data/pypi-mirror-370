from gllm_inference.schema import Vector as Vector
from gllm_inference.utils import preprocess_tei_input as preprocess_tei_input
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
from typing import Any
from typing_extensions import Self

class TEIEmbeddings(BaseModel, Embeddings):
    '''A custom LangChain `Embeddings` class to interact with Text Embeddings Inference (TEI).

    Attributes:
        url (str): The URL of the TEI service that hosts the embedding model.
        api_key (str | None, optional): The API key to the TEI service. Defaults to None.
        client (InferenceClient): The client instance to interact with the TEI service.
        query_prefix (str): The additional prefix to be added when embedding a query.
        document_prefix (str): The additional prefix to be added when embedding documents.

    Initialize with URL and API key example:
    ```python
    from gllm_inference.em_invoker.langchain import TEIEmbeddings

    embeddings = TEIEmbeddings(url="<url-to-tei-service>", api_key="<my-api-key>")
    ```

    Initialize with only URL example:
    ```python
    from gllm_inference.em_invoker.langchain import TEIEmbeddings

    embeddings = TEIEmbeddings(url="<url-to-tei-service>")
    ```

    Initialize with client example:
    ```python
    from gllm_inference.em_invoker.langchain import TEIEmbeddings
    from huggingface_hub import InferenceClient

    client = InferenceClient(model="<url-to-tei-service>", api_key="<my-api-key>")
    embeddings = TEIEmbeddings(client=client)
    ```
    '''
    url: str | None
    api_key: str | None
    client: Any
    query_prefix: str
    document_prefix: str
    def validate_environment(self) -> Self:
        """Validates that the TEI service URL and python package exists in environment.

        The validation is done in the following order:
        1. If neither `url` nor `client` is provided, an error will be raised.
        2. If an invalid `client` is provided, an error will be raised.
        3. If `url` is provided, it will be used to initialize the TEI service, along with an optional `api_key`.
        """
    def embed_documents(self, texts: list[str]) -> list[Vector]:
        """Embed documents using TEI's hosted embedding model.

        Args:
            texts (list[str]): The list of texts to embed.

        Returns:
            list[Vector]: List of embeddings, one for each text.
        """
    def embed_query(self, text: str) -> Vector:
        """Embed query using TEI's hosted embedding model.

        Args:
            text (str): The text to embed.

        Returns:
            Vector: Embeddings for the text.
        """
