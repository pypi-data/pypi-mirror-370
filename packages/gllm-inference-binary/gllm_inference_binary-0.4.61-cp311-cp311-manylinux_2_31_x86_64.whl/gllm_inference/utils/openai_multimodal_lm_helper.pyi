from _typeshed import Incomplete
from gllm_inference.utils.utils import get_mime_type as get_mime_type, is_local_file_path as is_local_file_path, is_remote_file_path as is_remote_file_path
from typing import Any

VALID_EXTENSIONS: Incomplete

def parse_prompt(prompt: list[tuple[str, list[str | bytes]]]) -> list[dict[str, Any]]:
    """Parses the prompt into a list of dictionaries, each representing a message.

    This method is responsible for converting the input prompt into a format that is compatible with OpenAI's API.

    Args:
        prompt (list[tuple[str, list[str | bytes]]]): The input prompt as a list of tuples containing
            role-content list pairs. Content can be either text strings or image bytes.

    Returns:
        list[dict[str, Any]]: A list of dictionaries, each representing a message.
    """
def parse_content(content: str | bytes) -> dict[str, Any]:
    """Parses the content into a dictionary with the appropriate type and content key.

    Args:
        content (str | bytes): The content to parse.

    Returns:
        dict[str, Any]: A dictionary with the appropriate type and content key.
    """
def validate_content_type(content: Any) -> bool:
    """Validates that the content is either a string or bytes.

    Args:
        content (Any): The content to validate.

    Returns:
        bool: True if the content is either a string or bytes, False otherwise.
    """
