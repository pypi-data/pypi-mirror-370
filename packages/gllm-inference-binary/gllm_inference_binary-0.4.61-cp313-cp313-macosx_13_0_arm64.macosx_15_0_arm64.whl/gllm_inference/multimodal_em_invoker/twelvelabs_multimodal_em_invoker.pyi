from _typeshed import Incomplete
from gllm_inference.multimodal_em_invoker.multimodal_em_invoker import BaseMultimodalEMInvoker as BaseMultimodalEMInvoker
from gllm_inference.schema import Vector as Vector
from gllm_inference.utils import get_mime_type as get_mime_type, is_local_file_path as is_local_file_path, is_remote_file_path as is_remote_file_path

VALID_EXTENSION_MAP: Incomplete
VALID_EXTENSIONS: Incomplete
FILE_TYPE_KEY_MAP: Incomplete
DEFAULT_VIDEO_STATUS_CHECK_INTERVAL: int
DEPRECATION_MESSAGE: str

class TwelveLabsMultimodalEMInvoker(BaseMultimodalEMInvoker[str | bytes]):
    """A class to interact with multimodal embedding models hosted through TwelveLabs API endpoints.

    The `TwelveLabsMultimodalEMInvoker` class is responsible for invoking a multimodal embedding model using the
    TwelveLabs API. It uses the multimodal embedding model to transform a content or a list of contents
    into their vector representations.

    Attributes:
        client (TwelveLabs): The client for the TwelveLabs API.
        model_name (str): The name of the multimodal embedding model to be used.

    Notes:
        The `TwelveLabsMultimodalEMInvoker` currently supports the following contents:
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
            1. URL pointing to a video.
            2. Local video file path.
    """
    client: Incomplete
    model_name: Incomplete
    video_status_check_interval: Incomplete
    def __init__(self, model_name: str, api_key: str, video_status_check_interval: int = ...) -> None:
        """Initializes a new instance of the TwelveLabsMultimodalEMInvoker class.

        Args:
            model_name (str): The name of the multimodal embedding model to be used.
            api_key (str): The API key for the TwelveLabs API.
            video_status_check_interval (int, optional): The interval in seconds to check the status of the video
                embedding task. Defaults to DEFAULT_VIDEO_STATUS_CHECK_INTERVAL.
        """
