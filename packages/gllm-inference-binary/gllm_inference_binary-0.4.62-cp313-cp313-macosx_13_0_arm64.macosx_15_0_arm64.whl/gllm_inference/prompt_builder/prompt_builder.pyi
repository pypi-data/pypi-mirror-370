import abc
from _typeshed import Incomplete
from abc import ABC
from gllm_inference.constants import MESSAGE_TUPLE_LENGTH as MESSAGE_TUPLE_LENGTH
from gllm_inference.schema import Attachment as Attachment, MultimodalContent as MultimodalContent, MultimodalPrompt as MultimodalPrompt, PromptRole as PromptRole
from gllm_inference.utils import get_prompt_keys as get_prompt_keys, validate_prompt_builder_kwargs as validate_prompt_builder_kwargs
from typing import Any

__ALL__: str
DEPRECATION_MESSAGE: str

class PromptBuilder:
    """A prompt builder class used in Gen AI applications.

    Attributes:
        system_template (str): The system prompt template. May contain placeholders enclosed in curly braces `{}`.
        user_template (str): The user prompt template. May contain placeholders enclosed in curly braces `{}`.
        prompt_key_set (set[str]): A set of expected keys that must be present in the prompt templates.
        ignore_extra_keys (bool): Whether to ignore extra keys when formatting the prompt.
    """
    system_template: Incomplete
    user_template: Incomplete
    prompt_key_set: Incomplete
    ignore_extra_keys: Incomplete
    def __init__(self, system_template: str = '', user_template: str = '', ignore_extra_keys: bool = False) -> None:
        """Initializes a new instance of the PromptBuilder class.

        Args:
            system_template (str, optional): The system prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            user_template (str, optional): The user prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            ignore_extra_keys (bool, optional): Whether to ignore extra keys when formatting the prompt.
                Defaults to False.

        Raises:
            ValueError: If both `system_template` and `user_template` are empty.
        """
    def format(self, history: MultimodalPrompt | None = None, extra_contents: list[MultimodalContent] | None = None, attachments: list[Attachment] | None = None, **kwargs: Any) -> MultimodalPrompt:
        """Formats the prompt templates into a `MultimodalPrompt`.

        This method processes each prompt template, replacing the placeholders in the template content with the
        corresponding values from `kwargs`. If any required key is missing from `kwargs`, it raises a `ValueError`.
        It also handles the provided history and extra contents. It formats the prompt as a `MultimodalPrompt`.

        Args:
            history (MultimodalPrompt | None, optional): The optional history to be included in the prompt.
                Defaults to None.
            extra_contents (list[MultimodalContent] | None, optional): The optional extra contents to be included in
                the user message. Defaults to None.
            attachments (list[Attachment] | None, optional): Deprecated parameter to handle attachments.
                Will be removed in v0.5.0. Defaults to None.
            **kwargs (Any): A dictionary of placeholder values to be injected into the prompt templates.
                Values must be either a string or an object that can be serialized to a string.

        Returns:
            MultimodalPrompt: A multimodal prompt.

        Raises:
            ValueError: If a required key for the prompt template is missing from `kwargs`.
        """

class BasePromptBuilder(ABC, metaclass=abc.ABCMeta):
    """A base class for prompt builders used in Gen AI applications.

    Attributes:
        system_template (str): The system prompt template. May contain placeholders enclosed in curly braces `{}`.
        user_template (str): The user prompt template. May contain placeholders enclosed in curly braces `{}`.
        prompt_key_set (set[str]): A set of expected keys that must be present in the prompt templates.
        ignore_extra_keys (bool): Whether to ignore extra keys when formatting the prompt.
    """
    system_template: Incomplete
    user_template: Incomplete
    prompt_key_set: Incomplete
    ignore_extra_keys: Incomplete
    logger: Incomplete
    def __init__(self, system_template: str = '', user_template: str = '', ignore_extra_keys: bool = False) -> None:
        """Initializes a new instance of the BasePromptBuilder class.

        Args:
            system_template (str, optional): The system prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            user_template (str, optional): The user prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            ignore_extra_keys (bool, optional): Whether to ignore extra keys when formatting the prompt.
                Defaults to False.

        Raises:
            ValueError: If both `system_template` and `user_template` are empty.
        """
    def format_as_message_list(self, history: list[tuple[PromptRole, list[Any] | str]] | None = None, attachments: list[Attachment] | None = None, system_multimodal_contents: list[Any] | None = None, user_multimodal_contents: list[Any] | None = None, is_multimodal: bool | None = None, **kwargs: Any) -> list[tuple[PromptRole, list[Any] | str]]:
        """Formats the prompt templates as a list of message tuples (role, formatted content).

        This method processes each prompt template, replacing the placeholders in the template content with the
        corresponding values from `kwargs`. If a required key is missing from `kwargs`, it raises a `ValueError`. It
        returns a list of tuples, where each tuple consists of a role and the corresponding formatted prompt content.

        Args:
            history (list[tuple[PromptRole, list[Any] | str]] | None, optional): The optional chat history to be
                included in the prompt. Defaults to None.
            attachments (list[Attachment] | None, optional): The optional attachments to be included in the prompt.
                Defaults to None.
            system_multimodal_contents (list[Any] | None, optional): Deprecated parameter to handle attachments.
                Will be removed in v0.5.0. Defaults to None.
            user_multimodal_contents (list[Any] | None, optional): Deprecated parameter to handle attachments.
                Will be removed in v0.5.0. Defaults to None.
            is_multimodal (bool | None, optional): Whether the prompt supports multimodal inputs. Will be deprecated in
                v0.5.0, in which multimodality will always be True. Defaults to None.
            **kwargs (Any): A dictionary of placeholder values to be injected into the prompt templates.

        Returns:
            list[tuple[PromptRole, list[Any] | str]]: A list of tuples, each containing a role and the corresponding
                formatted prompt content.

        Raises:
            ValueError: If a required key for the prompt template is missing from `kwargs`.
            ValueError: If multimodal contents are provided when `is_multimodal` is False.
        """
    def format_as_string(self, history: list[tuple[PromptRole, str]] | None = None, **kwargs: Any) -> str:
        """Formats the prompt as a string.

        This method formats the prompt as a string by first converting the prompt templates to a list of messages and
        then formatting the message list as a string.

        Args:
            history (list[tuple[PromptRole, str]] | None, optional): The optional chat history to be included in the
                prompt. Defaults to None.
            **kwargs (Any): A dictionary of placeholder values to be injected into the prompt templates.

        Returns:
            str: The formatted prompt with the placeholders replaced by the provided values.

        Raises:
            ValueError: If any required key is missing or there are extra keys in the kwargs.
        """
    @property
    def compatible_model_list(self) -> list[str]:
        '''Returns the list of compatible models for the prompt builder.

        This property returns the set of models that the prompt builder is compatible with. If the builder is
        model-specific, it returns the list of models in `_compatible_model_list`. Otherwise, it returns a list
        containing `"All"` to indicate compatibility with all models.

        Returns:
            list[str]: A list of compatible model names, or `["All"]` if the prompt builder is not model-specific.
        '''
