from _typeshed import Incomplete
from gllm_inference.schema import PromptRole as PromptRole
from gllm_inference.utils import get_prompt_keys as get_prompt_keys, validate_prompt_builder_kwargs as validate_prompt_builder_kwargs
from typing import Any

DEPRECATION_MESSAGE: str

class MultimodalPromptBuilder:
    """A prompt builder that is compatible with multimodal language models.

    Attributes:
        system_template (str): The system prompt template. May contain placeholders enclosed in curly braces `{}`.
        user_template (str): The user prompt template. May contain placeholders enclosed in curly braces `{}`.
        prompt_key_set (set[str]): A set of expected keys that must be present in the prompt templates.

    WARNING: This module is deprecated. Please use `gllm_inference.prompt_builder` instead.
    This module will be removed in version 0.5.0.
    """
    system_template: Incomplete
    user_template: Incomplete
    prompt_key_set: Incomplete
    def __init__(self, system_template: str = '', user_template: str = '') -> None:
        """Initializes a new instance of the MultimodalPromptBuilder class.

        Args:
            system_template (str, optional): The system prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            user_template (str, optional): The user prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.

        Raises:
            ValueError: If both `system_template` and `user_template` are empty.
        """
    def format_as_message_list(self, history: list[tuple[PromptRole, list[Any]]] | None = None, system_multimodal_contents: list[Any] | None = None, user_multimodal_contents: list[Any] | None = None, **kwargs: Any) -> list[tuple[PromptRole, list[Any]]]:
        """Formats the prompt templates as a list of message tuples (role, formatted list of contents).

        This method processes each prompt template, replacing the placeholders in the template content with the
        corresponding values from `kwargs`. If a required key is missing from `kwargs`, it raises a `ValueError`. It
        returns a list of tuples, where each tuple consists of a role and the corresponding formatted list of contents,
        which may contain multimodal inputs.

        Args:
            history (list[tuple[PromptRole, list[Any]]] | None, optional): The optional chat history to be included in
                the prompt. Defaults to None.
            system_multimodal_contents (list[Any] | None, optional): The optional multimodal contents for the system
                prompt. Defaults to None.
            user_multimodal_contents (list[Any] | None, optional): The optional multimodal contents for the user
                prompt. Defaults to None.
            **kwargs (Any): A dictionary of placeholder values to be injected into the prompt templates.

        Returns:
            list[tuple[PromptRole, list[Any]]]: A list of tuples, each containing a role and the corresponding
                formatted list of contents, which may contain multimodal inputs.

        Raises:
            ValueError: If a required key for the prompt template is missing from `kwargs`.
        """
