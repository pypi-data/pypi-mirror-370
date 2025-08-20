from _typeshed import Incomplete
from enum import StrEnum
from gllm_core.event import EventEmitter as EventEmitter
from typing import Any

TEMPLATE_VALIDATOR_REGEX: Incomplete
logger: Incomplete

def get_basic_auth_headers(username: str, password: str) -> dict[str, str] | None:
    """Generates the headers required for Basic Authentication.

    This method creates a header dictionary using Basic Authentication scheme. It encodes the username and password
    constants into Base64 format and prepares them for HTTP header authentication.

    Returns:
        dict[str, str] | None: A dictionary containing the 'Authorization' header with Base64 encoded credentials.
            Returns `None` if both `username` and `password` are empty strings.
    """
def get_mime_type(content: bytes) -> str:
    """Determines the MIME type of the provided content.

    This method determines the MIME type of the provided content by using the `magic` library.

    Args:
        content (bytes): The content to determine the MIME type.

    Returns:
        str: The MIME type of the content.
    """
def get_prompt_keys(template: str) -> set[str]:
    """Extracts keys from a template string based on a regex pattern.

    This function searches the template for placeholders enclosed in single curly braces `{}` and ignores
    any placeholders within double curly braces `{{}}`. It returns a set of the unique keys found.

    Args:
        template (str): The template string containing placeholders.

    Returns:
        set[str]: A set of keys extracted from the template.
    """
async def invoke_google_multimodal_lm(client: Any, messages: list[dict[str, Any]], hyperparameters: dict[str, Any], event_emitter: EventEmitter | None) -> str:
    """Invokes the Google multimodal language model with the provided prompt and hyperparameters.

    This method processes the prompt using the input prompt and hyperparameters. It handles both standard and
    streaming invocation. Streaming mode is enabled if an event emitter is provided.

    Args:
        client (Any): The Google client instance. This could either be:
            1. A `google.generativeai.GenerativeModel` instance.
            2. A `vertexai.generative_models.GenerativeModel` instance.
        messages (list[dict[str, Any]]): The input messages to be sent to the model.
        hyperparameters (dict[str, Any]): A dictionary of hyperparameters for the model.
        event_emitter (EventEmitter | None): The event emitter for streaming tokens. If provided, streaming
            invocation is enabled. Defaults to None.

    Returns:
        str: The generated response from the model.
    """
def is_local_file_path(content: Any, valid_extensions: set[str]) -> bool:
    """Checks if the content is a local file path.

    This method checks if the content is a local file path by verifying that the content:
    1. Is a string.
    2. Is a valid existing file path.
    3. Has a valid extension defined in the `valid_extensions` set.

    Args:
        content (Any): The content to check.
        valid_extensions (set[str]): The set of valid extensions.

    Returns:
        bool: True if the content is a local file path with a valid extension, False otherwise.
    """
def is_remote_file_path(content: Any, valid_extensions: set[str]) -> bool:
    """Checks if the content is a remote file path.

    This method checks if the content is a remote file path by verifying that the content:
    1. Is a string.
    2. Is a URL with a valid scheme of `http` or `https`.
    3. Has a valid extension defined in the `valid_extensions` set.

    Args:
        content (Any): The content to check.
        valid_extensions (set[str]): The set of valid extensions.

    Returns:
        bool: True if the content is a remote file path with a valid extension, False otherwise.
    """
def is_valid_extension(content: str, valid_extensions: set[str]) -> bool:
    """Checks if the content has a valid extension.

    Args:
        content (str): The content to check.
        valid_extensions (set[str]): The set of valid extensions.

    Returns:
        bool: True if the content has a valid extension, False otherwise.
    """
def load_google_vertexai_project_id(credentials_path: str) -> str:
    """Loads the Google Vertex AI project ID from the credentials file.

    Args:
        credentials_path (str): The path to the credentials file.

    Returns:
        str: The Google Vertex AI project ID.
    """
def preprocess_tei_input(texts: list[str], prefix: str) -> list[str]:
    """Preprocesses TEI input texts by replacing newline characters with spaces and adding the prefix to the text.

    Args:
        texts (list[str]): The list of texts to preprocess.
        prefix (str): The prefix to add to the text.

    Returns:
        list[str]: The list of preprocessed texts.
    """
def validate_prompt_builder_kwargs(prompt_key_set: set[str], ignore_extra_keys: bool = False, **kwargs: Any) -> None:
    """Validates that the provided kwargs match the expected prompt keys exactly.

    This helper function checks if the provided kwargs contain all and only the keys required by the prompt templates.
    If any required key is missing or there are extra keys, it raises a `ValueError`.

    Args:
        prompt_key_set (set[str]): The set of required prompt keys.
        ignore_extra_keys (bool, optional): Whether to ignore extra keys. Defaults to False.
        **kwargs (Any): The keyword arguments to be validated against the required prompt keys.

    Raises:
        ValueError: If any required key is missing from or any extra key is present in the kwargs.
    """
def validate_string_enum(enum_type: type[StrEnum], value: str) -> None:
    """Validates that the provided value is a valid string enum value.

    Args:
        enum_type (type[StrEnum]): The type of the string enum.
        value (str): The value to validate.

    Raises:
        ValueError: If the provided value is not a valid string enum value.
    """
