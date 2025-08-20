from _typeshed import Incomplete
from gllm_core.schema import Chunk as Chunk
from gllm_inference.constants import DEFAULT_CONTENT_PLACEHOLDER_TYPE as DEFAULT_CONTENT_PLACEHOLDER_TYPE, HEX_REPR_LENGTH as HEX_REPR_LENGTH
from pydantic import BaseModel
from typing import Any

logger: Incomplete

class Attachment(BaseModel):
    """Defines a file attachment schema.

    Attributes:
        data (bytes): The content data of the file attachment.
        filename (str): The filename of the file attachment.
        mime_type (str): The mime type of the file attachment.
        extension (str): The extension of the file attachment.
        url (str | None): The URL of the file attachment. Defaults to None.
    """
    data: bytes
    filename: str
    mime_type: str
    extension: str
    url: str | None
    @classmethod
    def from_bytes(cls, bytes: bytes, filename: str | None = None) -> Attachment:
        """Creates an Attachment from bytes.

        Args:
            bytes (bytes): The bytes of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the extension.

        Returns:
            Attachment: The instantiated Attachment.
        """
    @classmethod
    def from_data_url(cls, data_url: str, filename: str | None = None) -> Attachment:
        """Creates an Attachment from a data URL (data:[mime/type];base64,[bytes]).

        Args:
            data_url (str): The data URL of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the mime type.

        Returns:
            Attachment: The instantiated Attachment.
        """
    @classmethod
    def from_url(cls, url: str, filename: str | None = None) -> Attachment:
        """Creates an Attachment from a URL.

        Args:
            url (str): The URL of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the URL.

        Returns:
            Attachment: The instantiated Attachment.
        """
    @classmethod
    def from_path(cls, path: str, filename: str | None = None) -> Attachment:
        """Creates an Attachment from a path.

        Args:
            path (str): The path to the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the path.

        Returns:
            Attachment: The instantiated Attachment.
        """
    def write_to_file(self, path: str | None = None) -> None:
        """Writes the Attachment to a file.

        Args:
            path (str | None, optional): The path to the file. Defaults to None,
                in which case the filename will be used as the path.
        """

class ContentPlaceholder(BaseModel):
    """Defines a content placeholder schema.

    The `ContentPlaceholder` represents a lazy-loaded content to be sent to the language model.
    The content must be converted into a supported content type before being sent to the language model.

    Attributes:
        type (str): The type of the content placeholder.
        metadata (dict[str, Any]): The metadata of the content placeholder.
    """
    type: str
    metadata: dict[str, Any]

class ToolCall(BaseModel):
    """Defines a tool call request when a language model decides to invoke a tool.

    Attributes:
        id (str): The ID of the tool call.
        name (str): The name of the tool.
        args (dict[str, Any]): The arguments of the tool call.
    """
    id: str
    name: str
    args: dict[str, Any]

class ToolResult(BaseModel):
    """Defines a tool result to be sent back to the language model.

    Attributes:
        id (str): The ID of the tool call.
        output (str): The output of the tool call.
    """
    id: str
    output: str

class Reasoning(BaseModel):
    """Defines a reasoning output when a language model is configured to use reasoning.

    Attributes:
        id (str): The ID of the reasoning output. Defaults to an empty string.
        reasoning (str): The reasoning text. Defaults to an empty string.
        type (str): The type of the reasoning output. Defaults to an empty string.
        data (str): The additional data of the reasoning output. Defaults to an empty string.
    """
    id: str
    reasoning: str
    type: str
    data: str

class CodeExecResult(BaseModel):
    """Defines a code execution result when a language model is configured to execute code.

    Attributes:
        id (str): The ID of the code execution. Defaults to an empty string.
        code (str): The executed code. Defaults to an empty string.
        output (list[str | Attachment]): The output of the executed code. Defaults to an empty list.
    """
    id: str
    code: str
    output: list[str | Attachment]

class TokenUsage(BaseModel):
    """Defines the token usage data structure of a language model.

    Attributes:
        input_tokens (int): The number of input tokens.
        output_tokens (int): The number of output tokens.
    """
    input_tokens: int
    output_tokens: int

class LMOutput(BaseModel):
    """Defines the output of a language model.

    Attributes:
        response (str): The text response. Defaults to an empty string.
        tool_calls (list[ToolCall]): The tool calls, if the language model decides to invoke tools.
            Defaults to an empty list.
        structured_output (dict[str, Any] | BaseModel | None): The structured output, if a response schema is defined
            for the language model. Defaults to None.
        token_usage (TokenUsage | None): The token usage analytics, if requested. Defaults to None.
        duration (float | None): The duration of the invocation in seconds, if requested. Defaults to None.
        finish_details (dict[str, Any]): The details about how the generation finished, if requested.
            Defaults to an empty dictionary.
        reasoning (list[Reasoning]): The reasoning, if the language model is configured to output reasoning.
            Defaults to an empty list.
        citations (list[Chunk]): The citations, if the language model outputs citations. Defaults to an empty list.
        code_exec_results (list[CodeExecResult]): The code execution results, if the language model decides to
            execute code. Defaults to an empty list.
    """
    response: str
    tool_calls: list[ToolCall]
    structured_output: dict[str, Any] | BaseModel | None
    token_usage: TokenUsage | None
    duration: float | None
    finish_details: dict[str, Any]
    reasoning: list[Reasoning]
    citations: list[Chunk]
    code_exec_results: list[CodeExecResult]
