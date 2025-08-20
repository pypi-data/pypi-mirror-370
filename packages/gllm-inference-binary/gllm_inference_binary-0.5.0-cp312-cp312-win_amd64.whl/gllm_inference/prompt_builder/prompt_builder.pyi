from _typeshed import Incomplete
from gllm_inference.schema import Message as Message, MessageContent as MessageContent, MessageRole as MessageRole
from typing import Any

KEY_EXTRACTOR_REGEX: Incomplete

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
    def format(self, history: list[Message] | None = None, extra_contents: list[MessageContent] | None = None, **kwargs: Any) -> list[Message]:
        """Formats the prompt templates into a list of messages.

        This method processes each prompt template, replacing the placeholders in the template content with the
        corresponding values from `kwargs`. If any required key is missing from `kwargs`, it raises a `ValueError`.
        It also handles the provided history and extra contents. It formats the prompt as a list of messages.

        Args:
            history (list[Message] | None, optional): The history to be included in the prompt. Defaults to None.
            extra_contents (list[MessageContent] | None, optional): The extra contents to be included in the user
                message. Defaults to None.
            **kwargs (Any): A dictionary of placeholder values to be injected into the prompt templates.
                Values must be either a string or an object that can be serialized to a string.

        Returns:
            list[Message]: A formatted list of messages.

        Raises:
            ValueError: If a required key for the prompt template is missing from `kwargs`.
        """
