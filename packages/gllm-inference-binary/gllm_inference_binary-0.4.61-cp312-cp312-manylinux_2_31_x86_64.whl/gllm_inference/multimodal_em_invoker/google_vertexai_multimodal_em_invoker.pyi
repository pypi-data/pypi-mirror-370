from _typeshed import Incomplete
from gllm_inference.multimodal_em_invoker.multimodal_em_invoker import BaseMultimodalEMInvoker as BaseMultimodalEMInvoker
from gllm_inference.schema import Vector as Vector
from gllm_inference.utils import get_mime_type as get_mime_type, is_local_file_path as is_local_file_path, is_remote_file_path as is_remote_file_path, load_google_vertexai_project_id as load_google_vertexai_project_id

VALID_EXTENSION_MAP: Incomplete
VALID_EXTENSIONS: Incomplete
FILE_TYPE_KEY_MAP: Incomplete
DEPRECATION_MESSAGE: str

class GoogleVertexAIMultimodalEMInvoker(BaseMultimodalEMInvoker[str | bytes]):
    """A class to interact with multimodal embedding models hosted through Google's Vertex AI API endpoints.

    The `GoogleVertexAIMultimodalEMInvoker` class is responsible for invoking a multimodal embedding model using the
    Google Vertex AI API. It uses the multimodal embedding model to transform a content or a list of contents
    into their vector representations.

    Attributes:
        model (MultiModalEmbeddingModel): The multimodal embedding model to be used for embedding the input content.
        embedding_dimension (int): The dimension of the embedding vector.

    Notes:
        In order to use the `GoogleVertexAIMultimodalEMInvoker`, a credentials JSON file for a Google Cloud service
        account with the Vertex AI API enabled must be provided. For more information on how to create the credentials
        file, please refer to the following pages:
        1. https://cloud.google.com/docs/authentication/application-default-credentials.
        2. https://developers.google.com/workspace/guides/create-credentials.

        The `GoogleVertexAIMultimodalEMInvoker` currently supports the following contents:
        1. Text, which can be passed as plain strings.
        2. Image, which can be passed as:
            1. Base64 encoded image bytes.
            2. URL pointing to an image.
            3. Local image file path.
        4. Video, which can be passed as:
            1. Base64 encoded video bytes.
            2. URL pointing to a video.
            3. Local video file path.
    """
    model: Incomplete
    embedding_dimension: Incomplete
    def __init__(self, model_name: str, credentials_path: str, project_id: str | None = None, location: str = 'us-central1', embedding_dimension: int = 1408) -> None:
        '''Initializes a new instance of the GoogleVertexAIMultimodalEMInvoker class.

        Args:
            model_name (str): The name of the multimodal embedding model to be used.
            credentials_path (str): The path to the Google Cloud service account credentials JSON file.
            project_id (str | None, optional): The Google Cloud project ID. Defaults to None, in which case the
                project ID will be loaded from the credentials file.
            location (str, optional): The location of the Google Cloud project. Defaults to "us-central1".
            embedding_dimension (int, optional): The dimension of the embedding vector. Defaults to 1408.
        '''
